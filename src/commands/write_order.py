"""
Orders (write-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from models.product import Product
from models.order_item import OrderItem
from models.order import Order
from queries.read_order import get_orders_from_mysql
from db import get_sqlalchemy_session, get_redis_conn

def add_order(user_id: int, items: list):
    """Insert order with items in MySQL, keep Redis in sync"""
    if not user_id or not items:
        raise ValueError("Vous devez indiquer au moins 1 utilisateur et 1 item pour chaque commande.")

    try:
        product_ids = []
        for item in items:
            product_ids.append(int(item['product_id']))
    except Exception as e:
        print(e)
        raise ValueError(f"L'ID Article n'est pas valide: {item['product_id']}")
    session = get_sqlalchemy_session()

    try:
        products_query = session.query(Product).filter(Product.id.in_(product_ids)).all()
        price_map = {product.id: product.price for product in products_query}
        total_amount = 0
        order_items_data = []
        
        for item in items:
            pid = int(item["product_id"])
            qty = float(item["quantity"])

            if not qty or qty <= 0:
                raise ValueError(f"Vous devez indiquer une quantité superieure à zéro.")

            if pid not in price_map:
                raise ValueError(f"Article ID {pid} n'est pas dans la base de données.")

            unit_price = price_map[pid]
            total_amount += unit_price * qty
            order_items_data.append({
                'product_id': pid,
                'quantity': qty,
                'unit_price': unit_price
            })
        
        new_order = Order(user_id=user_id, total_amount=total_amount)
        session.add(new_order)
        session.flush() 
        
        order_id = new_order.id

        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            session.add(order_item)

        session.commit()

        # Insertion automatique dans Redis pour synchronisation
        add_order_to_redis(order_id, user_id, total_amount, items)

        return order_id

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_order(order_id: int):
    """Delete order in MySQL, keep Redis in sync"""
    session = get_sqlalchemy_session()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        
        if order:
            session.delete(order)
            session.commit()

            # Suppression automatique dans Redis pour synchronisation
            delete_order_from_redis(order_id)
            return 1  
        else:
            return 0  
            
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_order_to_redis(order_id, user_id, total_amount, items):
    """Insert order to Redis"""
    try:
        r = get_redis_conn()
        order_key = f"order:{order_id}"
        
        # Stocker les données principales de la commande dans une hash
        order_data = {
            'id': str(order_id),
            'user_id': str(user_id),
            'total_amount': str(total_amount),
            'created_at': str(__import__('datetime').datetime.now())
        }
        
        # Utiliser hset pour stocker les données de la commande
        r.hset(order_key, mapping=order_data)
        
        # Ajouter l'ID de la commande dans le SET d'index pour pouvoir retrouver toutes les commandes
        r.sadd("orders", order_id)
        
        # Synchroniser les quantités vendues par produit pour le rapport des articles les plus vendus
        for item in items:
            product_id = int(item['product_id'])
            quantity = int(float(item['quantity']))  # Convertir en entier pour le compteur
            
            # Utiliser incrby pour mettre à jour la quantité vendue de chaque article
            r.incrby(f"product_sales:{product_id}", quantity)
        
        print(f"Commande {order_id} ajoutée à Redis avec synchronisation des ventes de produits")
        
    except Exception as e:
        print(f"Erreur lors de l'ajout à Redis : {e}")

def delete_order_from_redis(order_id):
    """Delete order from Redis"""
    try:
        r = get_redis_conn()
        order_key = f"order:{order_id}"
        
        # Avant de supprimer, récupérer les items de la commande depuis MySQL pour décrémenter les ventes
        from models.order_item import OrderItem
        session = get_sqlalchemy_session()
        try:
            order_items = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            # Décrémenter les compteurs de ventes pour chaque produit
            for item in order_items:
                quantity = int(item.quantity)
                r.decrby(f"product_sales:{item.product_id}", quantity)
                
        except Exception as e:
            print(f"Erreur lors de la décrémentation des ventes : {e}")
        finally:
            session.close()
        
        # Supprimer la commande principale
        deleted_order = r.delete(order_key)
        
        # Retirer l'ID de la commande du SET d'index
        r.srem("orders", order_id)
        
        if deleted_order > 0:
            print(f"Commande {order_id} supprimée de Redis avec décrémentation des ventes")
        else:
            print(f"Commande {order_id} non trouvée dans Redis")
            
    except Exception as e:
        print(f"Erreur lors de la suppression de Redis : {e}")

def sync_all_orders_to_redis():
    """ Sync orders from MySQL to Redis """
    print("Vérification de la synchronisation Redis...")
    r = get_redis_conn()
    orders_in_redis = r.keys("order:*")
    rows_added = 0
    
    try:
        if len(orders_in_redis) == 0:
            print("Redis est vide, synchronisation depuis MySQL...")
            # Récupérer toutes les commandes depuis MySQL
            orders_from_mysql = get_orders_from_mysql()
            
            # Utiliser une session pour récupérer les order_items
            from models.order_item import OrderItem
            session = get_sqlalchemy_session()
            
            try:
                for order in orders_from_mysql:
                    # Créer une clé unique pour chaque commande
                    order_key = f"order:{order.id}"
                    
                    # Stocker les données de la commande dans Redis comme hash
                    order_data = {
                        'id': str(order.id),
                        'user_id': str(order.user_id),
                        'total_amount': str(order.total_amount),
                        'created_at': str(getattr(order, 'created_at', ''))
                    }
                    
                    # Utiliser hset pour stocker toutes les données d'un coup
                    r.hset(order_key, mapping=order_data)
                    
                    # Ajouter l'ID de la commande dans le SET d'index
                    r.sadd("orders", order.id)
                    
                    # Synchroniser les compteurs de ventes pour les order_items
                    order_items = session.query(OrderItem).filter(OrderItem.order_id == order.id).all()
                    for item in order_items:
                        quantity = int(item.quantity)
                        r.incrby(f"product_sales:{item.product_id}", quantity)
                    
                    rows_added += 1
            finally:
                session.close()
            
            print(f"Synchronisation terminée : {rows_added} commandes ajoutées à Redis")
        else:
            print(f"Redis contient déjà {len(orders_in_redis)} commandes, pas de synchronisation nécessaire")
    except Exception as e:
        print(f"Erreur lors de la synchronisation : {e}")
        return 0
    
    return len(orders_in_redis) + rows_added