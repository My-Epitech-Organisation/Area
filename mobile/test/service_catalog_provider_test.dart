import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:mobile/providers/service_catalog_provider.dart';
import 'package:mobile/models/service.dart';
import 'package:mobile/services/services.dart';

// Generate mocks
@GenerateMocks([ServiceCatalogService])
import 'service_catalog_provider_test.mocks.dart';

void main() {
  group('ServiceCatalogProvider', () {
    late ServiceCatalogProvider provider;
    late MockServiceCatalogService mockService;

    setUp(() {
      provider = ServiceCatalogProvider();
      mockService = MockServiceCatalogService();
      // Note: In a real implementation, we'd inject the service
      // For now, we'll test the public interface
    });

    tearDown(() {
      provider.dispose();
    });

    test('initial state should be correct', () {
      expect(provider.services, isEmpty);
      expect(provider.isLoadingServices, false);
      expect(provider.error, isNull);
    });

    test('getActionsForService should return null for unknown service', () {
      expect(provider.getActionsForService('unknown'), isNull);
    });

    test('getReactionsForService should return null for unknown service', () {
      expect(provider.getReactionsForService('unknown'), isNull);
    });

    // Note: More comprehensive tests would require dependency injection
    // to mock the ServiceCatalogService. For now, we test the basic interface.

    test('provider should be properly disposed', () {
      final newProvider = ServiceCatalogProvider();
      expect(() => newProvider.dispose(), returnsNormally);
    });
  });

  group('ServiceCatalogProvider Integration Tests', () {
    // These tests would require setting up a test environment with
    // mocked HTTP responses. For now, we'll create basic structure tests.

    test('Service model integration', () {
      final service = Service(
        name: 'test',
        actions: [
          ServiceAction(name: 'action1', description: 'Test action'),
        ],
        reactions: [
          ServiceReaction(name: 'reaction1', description: 'Test reaction'),
        ],
      );

      expect(service.name, 'test');
      expect(service.actions.length, 1);
      expect(service.reactions.length, 1);
      expect(service.displayName, 'Test');
    });
  });
}