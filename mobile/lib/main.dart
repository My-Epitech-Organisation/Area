import 'package:flutter/material.dart';
import 'home_page.dart';
import 'pages/create_applet_page.dart';
import 'pages/my_applets_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AREA Mobile',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'AREA - Dashboard'),
      routes: {
        '/create_applet': (context) => const CreateAppletPage(),
        '/my_applets': (context) => const MyAppletsPage(),
      },
    );
  }
}
