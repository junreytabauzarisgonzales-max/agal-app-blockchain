import 'package:flutter/material.dart';

import '../shared/agal_widgets.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Help & Support')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: const [
        AgalSurface(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionLabel('Log a harvest'),
              Text(
                'Open Home → Log New Harvest. Select a species, enter the weight and save. A connection is only needed to sign in and sync.',
              ),
              SectionLabel('Prepare for pickup'),
              Text(
                'Open your batch and tap Start Drying, then Finish Drying when it is ready. Suppliers can then verify the batch and confirm receipt.',
              ),
              SectionLabel('Verify a batch'),
              Text(
                'Suppliers and buyers can open Batches, select a batch and check its provenance against Sepolia. Pending events will be verifiable after anchoring.',
              ),
              SectionLabel('Send a message offline'),
              Text(
                'Farmer messages are saved on the phone and sent when connected. If a contact has a phone number, use the SMS button to open your phone’s messaging app.',
              ),
              SectionLabel('Manage sync'),
              Text(
                'Tap the status banner or open Profile → Sync management. Sync Now retries pending records. Keep Agal open while syncing.',
              ),
            ],
          ),
        ),
      ],
    ),
  );
}
