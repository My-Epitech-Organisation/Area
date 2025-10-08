import 'package:flutter/material.dart';
import '../models/service.dart';
import '../widgets/service_header_card.dart';
import '../widgets/action_reaction_widgets.dart';
import '../widgets/state_widgets.dart';

class ServiceDetailsPage extends StatelessWidget {
  final Service service;

  const ServiceDetailsPage({
    super.key,
    required this.service,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(service.displayName),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Service Header
            ServiceHeaderCard(service: service),
            const SizedBox(height: 24),

            // Actions Section
            ActionReactionSection(
              title: 'Actions',
              items: service.actions.map((action) => ActionReactionCard(
                title: action.displayName,
                description: action.description,
                icon: Icons.play_arrow,
                iconColor: Colors.green,
              )).toList(),
            ),

            // Reactions Section
            ActionReactionSection(
              title: 'Reactions',
              items: service.reactions.map((reaction) => ActionReactionCard(
                title: reaction.displayName,
                description: reaction.description,
                icon: Icons.flash_on,
                iconColor: Colors.orange,
              )).toList(),
            ),

            // Empty State
            if (service.actions.isEmpty && service.reactions.isEmpty)
              const EmptyStateWidget(
                message: 'No actions or reactions available',
              ),
          ],
        ),
      ),
    );
  }
}