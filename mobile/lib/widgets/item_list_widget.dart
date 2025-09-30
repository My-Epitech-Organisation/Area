import 'package:flutter/material.dart';

class ItemListWidget extends StatefulWidget {
  const ItemListWidget({super.key});

  @override
  State<ItemListWidget> createState() => _ItemListWidgetState();
}

class _ItemListWidgetState extends State<ItemListWidget> {
  // Liste pour stocker les éléments ajoutés par l'utilisateur
  final List<String> _items = [];

  // Contrôleur pour le champ de texte
  final TextEditingController _textController = TextEditingController();

  // Fonction pour ajouter un élément à la liste
  void _addItem() {
    if (_textController.text.isNotEmpty) {
      setState(() {
        _items.add(_textController.text);
        _textController.clear(); // Vide le champ après ajout
      });
    }
  }

  // Fonction pour supprimer un élément de la liste
  void _removeItem(int index) {
    setState(() {
      _items.removeAt(index);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Section pour ajouter des éléments à une liste
        const Text(
          'Ajouter un élément à la liste :',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        TextField(
          controller: _textController,
          decoration: const InputDecoration(
            labelText: 'Entrez quelque chose',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 10),
        ElevatedButton(
          onPressed: _addItem,
          child: const Text('Ajouter'),
        ),
        const SizedBox(height: 20),
        // Affichage de la liste
        const Text(
          'Liste des éléments :',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: _items.length,
            itemBuilder: (context, index) {
              return ListTile(
                title: Text(_items[index]),
                trailing: IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: () => _removeItem(index),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}