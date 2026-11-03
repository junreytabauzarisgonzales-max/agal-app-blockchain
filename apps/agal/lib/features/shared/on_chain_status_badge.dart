import 'package:flutter/material.dart';

/// Surfaces whether an event's hash has actually been anchored on
/// HarvestLedger yet -- this is the whole point of the traceability story,
/// so it needs to be visible somewhere, not just a column in the database.
class OnChainStatusBadge extends StatelessWidget {
  const OnChainStatusBadge({super.key, required this.status});
  final String status;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    final (icon, label, color) = switch (status) {
      'anchored' => (
        Icons.verified_outlined,
        'Verified on-chain',
        colors.primary,
      ),
      'failed' => (Icons.error_outline, 'Anchor failed', colors.error),
      _ => (Icons.hourglass_top_outlined, 'Anchoring…', colors.outline),
    };

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: color),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
