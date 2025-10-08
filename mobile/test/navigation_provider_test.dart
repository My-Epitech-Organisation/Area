import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/providers/navigation_provider.dart';

void main() {
  group('NavigationProvider', () {
    late NavigationProvider navigationProvider;

    setUp(() {
      navigationProvider = NavigationProvider();
    });

    tearDown(() {
      navigationProvider.dispose();
    });

    test('initial currentPage should be 0', () {
      expect(navigationProvider.currentPage, 0);
    });

    test('updateCurrentPage should update currentPage', () {
      navigationProvider.updateCurrentPage(2);
      expect(navigationProvider.currentPage, 2);
    });

    test('updateCurrentPage should notify listeners', () {
      var notified = false;
      navigationProvider.addListener(() {
        notified = true;
      });

      navigationProvider.updateCurrentPage(1);

      expect(notified, true);
      expect(navigationProvider.currentPage, 1);
    });

    test('pageController should be properly configured', () {
      expect(navigationProvider.pageController, isA<PageController>());
      expect(navigationProvider.pageController.initialPage, 0);
    });

    test('dispose should work without errors', () {
      final newProvider = NavigationProvider();
      expect(() => newProvider.dispose(), returnsNormally);
    });

    test('multiple updateCurrentPage calls should work', () {
      navigationProvider.updateCurrentPage(1);
      expect(navigationProvider.currentPage, 1);

      navigationProvider.updateCurrentPage(3);
      expect(navigationProvider.currentPage, 3);

      navigationProvider.updateCurrentPage(0);
      expect(navigationProvider.currentPage, 0);
    });

    test('notifyListeners should be called when updating current page', () {
      var notified = false;
      navigationProvider.addListener(() {
        notified = true;
      });

      navigationProvider.updateCurrentPage(2);

      expect(notified, true);
      expect(navigationProvider.currentPage, 2);
    });
  });
}
