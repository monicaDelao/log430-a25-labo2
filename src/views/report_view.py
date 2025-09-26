"""
Report view
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from views.template_view import get_template, get_param
from controllers.order_controller import get_report_highest_spending_users
from controllers.user_controller import list_users

def show_highest_spending_users():
    """ Show report of highest spending users from Redis data """
    try:
        # Récupérer le rapport des plus gros acheteurs
        highest_spenders = get_report_highest_spending_users()
        
        # Récupérer les utilisateurs pour obtenir les noms
        users = list_users(999)
        user_names = {user.id: user.name for user in users}
        
        if isinstance(highest_spenders, str):
            # Cas d'erreur
            return get_template(f"<h2>Les plus gros acheteurs</h2><p>Erreur: {highest_spenders}</p>")
        
        if not highest_spenders:
            return get_template("<h2>Les plus gros acheteurs</h2><p>Aucune donnée disponible</p>")
        
        # Générer les lignes du tableau avec le nouveau format structuré
        report_rows = []
        for user_data in highest_spenders:
            user_name = user_names.get(user_data['user_id'], f"Utilisateur {user_data['user_id']}")
            report_rows.append(f"""
                <tr>
                    <td>{user_data['rank']}</td>
                    <td>{user_name}</td>
                    <td>${user_data['total_spent']:.2f}</td>
                    <td>{user_data['order_count']}</td>
                </tr>
            """)
        
        table_content = f"""
            <h2>Les plus gros acheteurs (Top 10)</h2>
            <p>Rapport généré depuis les données Redis</p>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Rang</th>
                        <th>Nom</th>
                        <th>Total dépensé</th>
                        <th>Nb commandes</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(report_rows)}
                </tbody>
            </table>
        """
        
        return get_template(table_content)
        
    except Exception as e:
        print(f"Erreur dans show_highest_spending_users: {e}")
        return get_template(f"<h2>Les plus gros acheteurs</h2><p>Erreur lors de la génération du rapport: {e}</p>")

def show_best_sellers():
    """ Show report of best selling products """
    try:
        from controllers.order_controller import get_report_most_sold_products
        
        # Récupérer les données du rapport
        products_data = get_report_most_sold_products()
        
        if not products_data or isinstance(products_data, str):
            # Si pas de données ou erreur, afficher un message
            message = products_data if isinstance(products_data, str) else "Aucune donnée disponible"
            html_content = f"<h2>Les articles les plus vendus</h2><p>{message}</p>"
            return get_template(html_content)
        
        # Construire le tableau HTML
        html_content = "<h2>Les articles les plus vendus</h2>"
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Rang</th>
                    <th>ID Produit</th>
                    <th>Nom du produit</th>
                    <th>Quantité vendue</th>
                    <th>Prix unitaire</th>
                    <th>Revenus totaux</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for product in products_data:
            html_content += f"""
                <tr>
                    <td>{product['rank']}</td>
                    <td>{product['product_id']}</td>
                    <td>{product['product_name']}</td>
                    <td>{product['quantity_sold']}</td>
                    <td>{product['price']:.2f} $</td>
                    <td>{product['total_revenue']:.2f} $</td>
                </tr>
            """
        
        html_content += """
            </tbody>
        </table>
        """
        
        return get_template(html_content)
        
    except Exception as e:
        print(f"Erreur dans show_best_sellers: {e}")
        return get_template(f"<h2>Les articles les plus vendus</h2><p>Erreur lors de la génération du rapport: {e}</p>")