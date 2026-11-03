import 'package:flutter/material.dart';

import 'widgets/legal_section.dart';

class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Privacy policy')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            Text(
              'Draft -- last updated September 2026. This is a working draft for the '
              'Philippine Startup Challenge and has not yet been reviewed by legal counsel.',
              style: TextStyle(
                fontSize: 12,
                color: Theme.of(context).colorScheme.outline,
              ),
            ),
            const SizedBox(height: 20),
            const LegalSection(
              title: 'What we collect',
              body:
                  '• Account information: email address, full name, your chosen role (Farmer, '
                  'Supplier/Aggregator, or Buyer/Exporter), and optionally a phone number and municipality.\n\n'
                  '• Harvest and custody data: batch details (species, estimated weight, harvest '
                  'location and date) and chain-of-custody events (drying, transfers, notes) that you or '
                  'another role in the same supply chain records.\n\n'
                  '• Messages: the content of chats you send to other Agal users, and who you sent them to.\n\n'
                  '• Price data: prices posted by Suppliers/Aggregators and Buyers/Exporters, along with '
                  'which account posted them.',
            ),
            const LegalSection(
              title: "What we don't collect",
              body: 'Agal does not use third-party advertising trackers, and does not sell your data.',
            ),
            const LegalSection(
              title: 'What goes on the public blockchain',
              body:
                  'Chain-of-custody events are anchored on a public blockchain ledger so their history can '
                  'be independently verified. Only a cryptographic hash of each event is published on-chain '
                  '-- never your name, contact details, prices, messages, or the plain content of the event. '
                  'Your account and batch data stay in Agal\'s own database; the blockchain only ever sees an '
                  'opaque fingerprint of it.',
            ),
            const LegalSection(
              title: 'Who can see your data',
              body:
                  'Batch and chain-of-custody information is visible to the roles involved in that batch\'s '
                  'supply chain, since traceability is the point of the Service. Price data you post is '
                  'visible to other Agal users so that pricing stays transparent. Messages are only visible '
                  'to you and the person you\'re messaging. Your account credentials are never shared.',
            ),
            const LegalSection(
              title: 'Sending a message via SMS',
              body:
                  'If you choose to send a message via SMS instead of in-app, that message is handed off to '
                  'your phone\'s own default messaging app -- Agal does not see, store, or have access to '
                  'anything sent that way.',
            ),
            const LegalSection(
              title: 'Data retention',
              body:
                  'We retain account and batch data for as long as your account is active. Chain-of-custody '
                  'hashes anchored on the public blockchain cannot be deleted once recorded, as described in '
                  'our Terms of Use.',
            ),
            const LegalSection(
              title: 'Contact',
              body:
                  'Questions about this policy can be directed to the Agal team through the channels '
                  'announced on the Agal website\'s news page.',
            ),
          ],
        ),
      ),
    );
  }
}
