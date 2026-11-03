import 'package:flutter/material.dart';

import '../chat/chat_list_screen.dart';
import '../settings/profile_screen.dart';
import '../shared/role_shell.dart';
import '../shared/verification_screen.dart';
import 'supplier_home_screen.dart';

/// The Supplier's bottom-nav shell: Home (incoming-inventory dashboard),
/// Messages, Verification (look up/verify any batch against Sepolia), Settings.
class SupplierShellScreen extends StatelessWidget {
  const SupplierShellScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const RoleShell(
      tabs: [
        ShellTab(
          label: 'Home',
          icon: Icons.home_outlined,
          child: SupplierHomeScreen(),
        ),
        ShellTab(
          label: 'Batches',
          icon: Icons.inventory_2_outlined,
          child: VerificationScreen(),
        ),
        ShellTab(
          label: 'Messages',
          icon: Icons.chat_bubble_outline,
          child: ChatListScreen(),
          showBadge: true,
        ),
        ShellTab(
          label: 'Profile',
          icon: Icons.person_outline,
          child: ProfileScreen(),
        ),
      ],
    );
  }
}
