import 'package:flutter/material.dart';
import 'widgets/counter_widget.dart'; // Import du widget compteur séparé
import 'widgets/item_list_widget.dart'; // Import du widget liste séparé

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  // Cette classe est la configuration pour l'état. Elle contient les valeurs
  // (dans ce cas le titre) fournies par le parent et utilisées par la méthode build de l'État.
  // Les champs dans une sous-classe Widget sont toujours marqués "final".

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    // Cette méthode est réexécutée chaque fois que setState est appelée.
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            // Utilisation du widget compteur séparé
            const CounterWidget(),
            const SizedBox(height: 20),
            // Utilisation du widget liste séparé
            const Expanded(child: ItemListWidget()),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Ici, on pourrait incrémenter le compteur du widget CounterWidget,
          // mais pour la simplicité, on laisse comme ça.
        },
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}