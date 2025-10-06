import 'package:flutter/material.dart';

class MyAppletsPage extends StatelessWidget {
  const MyAppletsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('My Applets')),
      body: Center(child: Text('List of my applets here')),
    );
  }
}
