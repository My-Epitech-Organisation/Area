import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/widgets/state_widgets.dart';

void main() {
  group('LoadingStateWidget', () {
    testWidgets('should display CircularProgressIndicator', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LoadingStateWidget(),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });

  group('ErrorStateWidget', () {
    testWidgets('should display error message', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ErrorStateWidget(),
          ),
        ),
      );

      expect(find.text('An error occurred'), findsOneWidget);
    });

    testWidgets('should display retry button when callback provided', (WidgetTester tester) async {
      var called = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ErrorStateWidget(onRetry: () => called = true),
          ),
        ),
      );

      expect(find.text('Retry'), findsOneWidget);
      await tester.tap(find.text('Retry'));
      expect(called, true);
    });
  });

  group('EmptyStateWidget', () {
    testWidgets('should display message', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyStateWidget(message: 'No data'),
          ),
        ),
      );

      expect(find.text('No data'), findsOneWidget);
    });
  });
}