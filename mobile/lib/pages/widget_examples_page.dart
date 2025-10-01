import 'package:flutter/material.dart';
import '../widgets/widget_examples.dart';

class WidgetExamplesPage extends StatelessWidget {
  const WidgetExamplesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Les Widgets en Flutter',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Les widgets sont les composants de base de Flutter. Ils sont similaires aux composants React :\n\n'
                '• Ils décrivent l\'apparence de l\'interface\n'
                '• Ils peuvent recevoir des propriétés (props)\n'
                '• Ils peuvent être réutilisables\n'
                '• Ils forment une arborescence (widget tree)',
                style: TextStyle(fontSize: 16, height: 1.5),
              ),
              const SizedBox(height: 24),
              const Text(
                'Types de Widgets :',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),

              // Exemple 1: Stateless Widget
              const Text(
                '1. StatelessWidget - Sans état',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Comme un composant React fonctionnel. Il ne change pas d\'état interne.',
              ),
              const SizedBox(height: 12),
              const SimpleCard(
                title: 'Carte Simple',
                description: 'Ceci est un widget stateless qui affiche du contenu statique.',
                color: Colors.blue,
              ),

              const SizedBox(height: 24),

              // Exemple 2: Stateful Widget
              const Text(
                '2. StatefulWidget - Avec état',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Comme un composant React avec useState. Il peut changer son apparence.',
              ),
              const SizedBox(height: 12),
              InteractiveButton(
                label: 'Changez ma couleur !',
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('État changé !')),
                  );
                },
              ),

              const SizedBox(height: 24),

              // Exemple 3: Widget composite
              const Text(
                '3. Widget Composite',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.purple,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Combine plusieurs widgets pour créer des composants plus complexes.',
              ),
              const SizedBox(height: 12),
              const UserProfileCard(
                name: 'Marie Martin',
                email: 'marie@example.com',
                avatarUrl: 'https://via.placeholder.com/150/FF6B6B/FFFFFF?text=M',
              ),

              const SizedBox(height: 24),

              // Comparaison avec React
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Comparaison avec React :',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text('• Widget Flutter = Composant React'),
                    Text('• StatelessWidget = Fonction React'),
                    Text('• StatefulWidget = Classe React avec state'),
                    Text('• props = paramètres du constructeur'),
                    Text('• setState() = useState()'),
                    Text('• build() = return JSX'),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Instruction pour la navigation
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.swipe, color: Colors.blue),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Utilisez le swipe ou la barre de navigation pour changer de page',
                        style: TextStyle(color: Colors.blue),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
  }
}