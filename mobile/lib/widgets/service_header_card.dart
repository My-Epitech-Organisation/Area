import 'package:flutter/material.dart';
import '../models/service.dart';

class ServiceHeaderCard extends StatelessWidget {
  final Service service;

  const ServiceHeaderCard({
    super.key,
    required this.service,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                _getServiceIcon(service.name),
                color: Theme.of(context).primaryColor,
                size: 32,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    service.displayName,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${service.actions.length} actions • ${service.reactions.length} reactions',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getServiceIcon(String serviceName) {
    switch (serviceName.toLowerCase()) {
      case 'facebook':
        return Icons.facebook;
      case 'twitter':
      case 'x':
        return Icons.alternate_email;
      case 'gmail':
      case 'email':
        return Icons.email;
      case 'discord':
        return Icons.chat;
      case 'github':
        return Icons.code;
      case 'spotify':
        return Icons.music_note;
      case 'youtube':
        return Icons.play_circle_fill;
      case 'slack':
        return Icons.message;
      case 'telegram':
        return Icons.send;
      case 'weather':
        return Icons.wb_sunny;
      case 'timer':
        return Icons.timer;
      case 'rss':
        return Icons.rss_feed;
      default:
        return Icons.apps;
    }
  }
}
