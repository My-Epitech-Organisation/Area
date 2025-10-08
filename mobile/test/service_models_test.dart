import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/service.dart';

void main() {
  group('Service Model', () {
    test('Service.fromJson should parse valid JSON correctly', () {
      final json = {
        'name': 'github',
        'actions': [
          {
            'name': 'new_issue',
            'description': 'Triggered when a new issue is created'
          }
        ],
        'reactions': [
          {
            'name': 'create_issue',
            'description': 'Creates a new issue in the repository'
          }
        ]
      };

      final service = Service.fromJson(json);

      expect(service.name, 'github');
      expect(service.actions.length, 1);
      expect(service.reactions.length, 1);
      expect(service.actions[0].name, 'new_issue');
      expect(service.reactions[0].name, 'create_issue');
    });

    test('Service.fromJson should handle null values gracefully', () {
      final json = {
        'name': null,
        'actions': null,
        'reactions': null
      };

      final service = Service.fromJson(json);

      expect(service.name, '');
      expect(service.actions, isEmpty);
      expect(service.reactions, isEmpty);
    });

    test('Service.fromJson should handle empty JSON', () {
      final json = <String, dynamic>{};

      final service = Service.fromJson(json);

      expect(service.name, '');
      expect(service.actions, isEmpty);
      expect(service.reactions, isEmpty);
    });

    test('Service.toJson should serialize correctly', () {
      final service = Service(
        name: 'discord',
        actions: [
          ServiceAction(name: 'message_received', description: 'When a message is received')
        ],
        reactions: [
          ServiceReaction(name: 'send_message', description: 'Send a message to a channel')
        ],
      );

      final json = service.toJson();

      expect(json['name'], 'discord');
      expect(json['actions'], isA<List>());
      expect(json['reactions'], isA<List>());
      expect((json['actions'] as List).length, 1);
      expect((json['reactions'] as List).length, 1);
    });

    test('Service.displayName should format names correctly', () {
      expect(Service(name: 'github', actions: [], reactions: []).displayName, 'Github');
      expect(Service(name: 'discord_bot', actions: [], reactions: []).displayName, 'Discord Bot');
      expect(Service(name: '', actions: [], reactions: []).displayName, 'Unknown Service');
      expect(Service(name: 'test_service', actions: [], reactions: []).displayName, 'Test Service');
    });

    test('Service.iconPath should return correct path', () {
      final service = Service(name: 'github', actions: [], reactions: []);
      expect(service.iconPath, 'assets/icons/github.png');
    });
  });

  group('ServiceAction Model', () {
    test('ServiceAction.fromJson should parse correctly', () {
      final json = {
        'name': 'new_commit',
        'description': 'Triggered when a new commit is pushed'
      };

      final action = ServiceAction.fromJson(json);

      expect(action.name, 'new_commit');
      expect(action.description, 'Triggered when a new commit is pushed');
    });

    test('ServiceAction.fromJson should handle null values', () {
      final json = {
        'name': null,
        'description': null
      };

      final action = ServiceAction.fromJson(json);

      expect(action.name, '');
      expect(action.description, '');
    });

    test('ServiceAction.toJson should serialize correctly', () {
      final action = ServiceAction(
        name: 'pull_request_opened',
        description: 'When a pull request is opened'
      );

      final json = action.toJson();

      expect(json['name'], 'pull_request_opened');
      expect(json['description'], 'When a pull request is opened');
    });
  });

  group('ServiceReaction Model', () {
    test('ServiceReaction.fromJson should parse correctly', () {
      final json = {
        'name': 'send_notification',
        'description': 'Sends a notification to the user'
      };

      final reaction = ServiceReaction.fromJson(json);

      expect(reaction.name, 'send_notification');
      expect(reaction.description, 'Sends a notification to the user');
    });

    test('ServiceReaction.fromJson should handle null values', () {
      final json = {
        'name': null,
        'description': null
      };

      final reaction = ServiceReaction.fromJson(json);

      expect(reaction.name, '');
      expect(reaction.description, '');
    });

    test('ServiceReaction.toJson should serialize correctly', () {
      final reaction = ServiceReaction(
        name: 'create_comment',
        description: 'Creates a comment on the issue'
      );

      final json = reaction.toJson();

      expect(json['name'], 'create_comment');
      expect(json['description'], 'Creates a comment on the issue');
    });
  });
}