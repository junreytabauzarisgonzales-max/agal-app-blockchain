import 'package:flutter/material.dart';

import 'widgets/legal_section.dart';

class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Terms of use')),
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
              title: '1. Acceptance of these terms',
              body:
                  'By creating an account or using the Agal mobile app or website (together, the '
                  '"Service"), you agree to these Terms of Use. If you do not agree, please do not use the Service.',
            ),
            const LegalSection(
              title: '2. Who can use Agal',
              body:
                  'Agal is intended for farmers, aggregators/suppliers, and buyers/exporters participating '
                  'in the seaweed supply chain. You are responsible for choosing the role that accurately '
                  'describes you when you register, and for keeping your account credentials confidential.',
            ),
            const LegalSection(
              title: '3. Accuracy of information you submit',
              body:
                  'Harvest batch details, chain-of-custody events, and price records you enter are your '
                  'responsibility. Agal does not independently verify weights, prices, or locations you submit '
                  '-- it records what you enter and makes that record tamper-evident, not necessarily accurate '
                  'at the point of entry.',
            ),
            const LegalSection(
              title: '4. Blockchain records are permanent',
              body:
                  'A cryptographic hash of each chain-of-custody event is anchored on a public blockchain '
                  'ledger. Once anchored, that record cannot be edited or deleted by Agal or by you -- that '
                  'permanence is what makes the history verifiable. Do not submit anything you would not want '
                  'permanently, verifiably recorded as having occurred at that time.',
            ),
            const LegalSection(
              title: '5. Acceptable use',
              body:
                  'You agree not to use the Service to submit false chain-of-custody or price information, '
                  'to interfere with the Service\'s operation, or to attempt to access accounts or data that '
                  'are not yours.',
            ),
            const LegalSection(
              title: '6. Service availability',
              body:
                  'Agal is provided on an "as is" basis while under active development for the Philippine '
                  'Startup Challenge. Features, availability, and these terms may change as the Service evolves.',
            ),
            const LegalSection(
              title: '7. Contact',
              body:
                  'Questions about these terms can be directed to the Agal team through the channels '
                  'announced on the Agal website\'s news page.',
            ),
          ],
        ),
      ),
    );
  }
}
