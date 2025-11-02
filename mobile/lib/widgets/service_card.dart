import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../models/service.dart';
import '../utils/service_icons.dart';

class ServiceCard extends StatelessWidget {
  final Service service;
  final VoidCallback? onTap;

  const ServiceCard({super.key, required this.service, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              // Service Icon/Logo
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: service.logo != null
                    ? SvgPicture.network(
                        service.logo!,
                        width: 24,
                        height: 24,
                        placeholderBuilder: (context) => Icon(
                          ServiceIcons.getServiceIcon(service.name),
                          color: Theme.of(context).primaryColor,
                          size: 24,
                        ),
                        errorBuilder: (context, error, stackTrace) => Icon(
                          ServiceIcons.getServiceIcon(service.name),
                          color: Theme.of(context).primaryColor,
                          size: 24,
                        ),
                      )
                    : Icon(
                        ServiceIcons.getServiceIcon(service.name),
                        color: Theme.of(context).primaryColor,
                        size: 24,
                      ),
              ),
              const SizedBox(width: 16),

              // Service Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      service.displayName,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${service.actions.length} actions, ${service.reactions.length} reactions',
                      style: Theme.of(
                        context,
                      ).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),

              // Arrow Icon
              Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey[400]),
            ],
          ),
        ),
      ),
    );
  }
}
