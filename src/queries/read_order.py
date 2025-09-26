"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from db import get_sqlalchemy_session, get_redis_conn
from sqlalchemy import desc
from models.order import Order

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    return r.hgetall(f"order:{order_id}")

def get_orders_from_mysql(limit=9999):
    """Get last X orders"""
    session = get_sqlalchemy_session()
    return session.query(Order).order_by(desc(Order.id)).limit(limit).all()

def get_orders_from_redis(limit=9999):
    """Get last X orders from Redis"""
    try:
        r = get_redis_conn()
        
        # Récupérer tous les IDs de commandes depuis le SET
        order_ids = r.smembers("orders")
        
        if not order_ids:
            return []
        
        # Convertir en entiers et trier par ID décroissant (les plus récents en premier)
        # Décoder les bytes si nécessaire
        decoded_ids = []
        for order_id in order_ids:
            if isinstance(order_id, bytes):
                decoded_ids.append(int(order_id.decode('utf-8')))
            else:
                decoded_ids.append(int(order_id))
        order_ids = sorted(decoded_ids, reverse=True)
        
        # Limiter le nombre de résultats
        order_ids = order_ids[:limit]
        
        # Récupérer les données de chaque commande
        orders = []
        for order_id in order_ids:
            order_key = f"order:{order_id}"
            order_data = r.hgetall(order_key)
            
            if order_data:
                # Créer un objet simple pour simuler les attributs de l'objet Order
                class OrderFromRedis:
                    def __init__(self, data):
                        # Décoder les bytes de Redis avant conversion
                        self.id = int(data.get('id', b'0').decode('utf-8'))
                        self.user_id = int(data.get('user_id', b'0').decode('utf-8'))
                        self.total_amount = float(data.get('total_amount', b'0.0').decode('utf-8'))
                        self.created_at = data.get('created_at', b'').decode('utf-8')
                
                orders.append(OrderFromRedis(order_data))
        
        return orders
        
    except Exception as e:
        print(f"Erreur lors de la lecture depuis Redis : {e}")
        return []

def get_highest_spending_users():
    """Get report of highest spending users from Redis data - format structuré pour HTML"""
    try:
        from collections import defaultdict
        
        # Récupérer toutes les commandes depuis Redis
        orders = get_orders_from_redis()
        
        print(f"[DEBUG] Nombre de commandes récupérées: {len(orders) if orders else 0}")
        if orders:
            for order in orders:
                print(f"[DEBUG] Order ID: {order.id}, User ID: {order.user_id}, Total: {order.total_amount}")
        
        if not orders:
            print("[DEBUG] Aucune commande trouvée dans Redis")
            return []
        
        # Calculer les dépenses par utilisateur
        expenses_by_user = defaultdict(float)
        for order in orders:
            expenses_by_user[order.user_id] += order.total_amount
        
        # Trier par total dépensé (ordre décroissant) et prendre le top 10
        highest_spending_users = sorted(expenses_by_user.items(), key=lambda item: item[1], reverse=True)[:10]
        
        # Convertir en format structuré (liste de dictionnaires)
        structured_report = []
        for rank, (user_id, total_spent) in enumerate(highest_spending_users, 1):
            structured_report.append({
                'rank': rank,
                'user_id': user_id,
                'total_spent': total_spent,
                'order_count': sum(1 for order in orders if order.user_id == user_id)
            })
        
        return structured_report
        
    except Exception as e:
        print(f"Erreur lors de la génération du rapport : {e}")
        return []

def get_most_sold_products():
    """Get report of most sold products from Redis data - format structuré pour HTML"""
    try:
        r = get_redis_conn()
        
        # Récupérer tous les compteurs de ventes de produits depuis Redis
        product_sales_keys = r.keys("product_sales:*")
        
        if not product_sales_keys:
            print("[DEBUG] Aucun compteur de ventes trouvé dans Redis")
            return []
        
        # Construire la liste des produits avec leurs quantités vendues
        product_sales = []
        session = get_sqlalchemy_session()
        
        try:
            from models.product import Product
            
            for key in product_sales_keys:
                # Extraire l'ID du produit depuis la clé
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                product_id = int(key_str.split(':')[1])
                
                # Récupérer la quantité vendue depuis Redis
                quantity_sold = int(r.get(key) or 0)
                
                if quantity_sold > 0:
                    # Récupérer les informations du produit depuis MySQL
                    product = session.query(Product).filter(Product.id == product_id).first()
                    
                    if product:
                        product_sales.append({
                            'product_id': product_id,
                            'product_name': product.name,
                            'quantity_sold': quantity_sold,
                            'price': float(product.price),
                            'total_revenue': quantity_sold * float(product.price)
                        })
            
            # Trier par quantité vendue (ordre décroissant)
            product_sales.sort(key=lambda x: x['quantity_sold'], reverse=True)
            
            # Ajouter un rang pour chaque produit
            for rank, product in enumerate(product_sales, 1):
                product['rank'] = rank
            
            return product_sales[:10]  # Top 10 des articles les plus vendus
            
        finally:
            session.close()
        
    except Exception as e:
        print(f"Erreur lors de la génération du rapport des articles les plus vendus : {e}")
        return []