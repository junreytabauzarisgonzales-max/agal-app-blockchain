import 'package:flutter/material.dart';

import '../chat/chat_list_screen.dart';
import '../settings/profile_screen.dart';
import '../shared/role_shell.dart';
import '../shared/verification_screen.dart';
import 'buyer_home_screen.dart';

/// The Buyer's bottom-nav shell: Home (marketplace), Messages, Verification
/// (look up/verify any batch against Sepolia before buying), Settings.
class BuyerShellScreen extends StatelessWidget {
  const BuyerShellScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const RoleShell(
      tabs: [
        ShellTab(
          label: 'Home',
          icon: Icons.home_outlined,
          child: BuyerHomeScreen(),
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
