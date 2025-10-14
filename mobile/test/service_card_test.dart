import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/service.dart';
import 'package:mobile/widgets/service_card.dart';

void main() {
  group('ServiceCard', () {
    late Service testService;

    setUp(() {
      testService = Service(id: 1, name: 'github', actions: [], reactions: []);
    });

    testWidgets('should display service name correctly', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ServiceCard(service: testService)),
        ),
      );

      expect(find.text('Github'), findsOneWidget);
    });

    testWidgets('should display actions and reactions count', (
      WidgetTester tester,
    ) async {
      final serviceWithData = Service(
        id: 2,
        name: 'discord',
        actions: [
          ServiceAction(
            id: 1,
            name: 'message_received',
            description: 'Message received',
          ),
          ServiceAction(id: 2, name: 'user_joined', description: 'User joined'),
        ],
        reactions: [
          ServiceReaction(
            id: 3,
            name: 'send_message',
            description: 'Send message',
          ),
        ],
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ServiceCard(service: serviceWithData)),
        ),
      );

      expect(find.text('2 actions, 1 reactions'), findsOneWidget);
    });

    testWidgets('should display correct icon for known services', (
      WidgetTester tester,
    ) async {
      final services = [
        Service(id: 1, name: 'github', actions: [], reactions: []),
        Service(id: 2, name: 'discord', actions: [], reactions: []),
        Service(id: 3, name: 'unknown', actions: [], reactions: []),
      ];

      for (final service in services) {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(body: ServiceCard(service: service)),
          ),
        );

        // Check that there are icons displayed (service icon + arrow icon)
        expect(find.byType(Icon), findsNWidgets(2));
        await tester.pumpAndSettle();
      }
    });

    testWidgets('should call onTap when tapped', (WidgetTester tester) async {
      var tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ServiceCard(service: testService, onTap: () => tapped = true),
          ),
        ),
      );

      await tester.tap(find.byType(InkWell));
      expect(tapped, true);
    });

    testWidgets('should not be tappable when onTap is null', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ServiceCard(service: testService)),
        ),
      );

      final inkWell = tester.widget<InkWell>(find.byType(InkWell));
      expect(inkWell.onTap, isNull);
    });

    testWidgets('should have correct card styling', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ServiceCard(service: testService)),
        ),
      );

      final card = tester.widget<Card>(find.byType(Card));
      expect(card.elevation, 4);
      expect(card.shape, isA<RoundedRectangleBorder>());
    });

    testWidgets('should display service icon in colored container', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ServiceCard(service: testService)),
        ),
      );

      expect(
        find.byType(Container),
        findsWidgets,
      ); // Icon container and main container
      final icons = tester.widgetList<Icon>(find.byType(Icon));
      expect(icons.length, 2); // Service icon and arrow icon
      expect(icons.first.size, 24); // Service icon size
    });
  });
}
