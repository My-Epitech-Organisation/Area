// Simple Flutter widget test for the AREA Mobile app.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Basic widget test', (WidgetTester tester) async {
    // Test a simple widget to ensure the test framework works
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('Test')),
          body: const Center(child: Text('Hello World')),
        ),
      ),
    );

    // Verify the test widget is displayed
    expect(find.text('Test'), findsOneWidget);
    expect(find.text('Hello World'), findsOneWidget);
  });

  testWidgets('Material app creation test', (WidgetTester tester) async {
    // Create a simple MaterialApp to test basic functionality
    const testApp = MaterialApp(
      title: 'Test App',
      home: Scaffold(
        body: Center(child: Text('Test Content')),
      ),
    );

    await tester.pumpWidget(testApp);

    // Verify the MaterialApp works
    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.text('Test Content'), findsOneWidget);
  });
}
