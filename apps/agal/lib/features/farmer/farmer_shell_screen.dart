import 'package:flutter/material.dart';

import '../chat/chat_list_screen.dart';
import '../settings/profile_screen.dart';
import '../shared/role_shell.dart';
import 'farmer_dashboard_screen.dart';
import 'farmer_home_screen.dart';

/// The Farmer's bottom-nav shell: Home (dashboard), Messages, Harvest (the
/// working batch list -- what used to be the sole "home" screen), Settings.
class FarmerShellScreen extends StatelessWidget {
  const FarmerShellScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const RoleShell(
      tabs: [
        ShellTab(
          label: 'Home',
          icon: Icons.home_outlined,
          child: FarmerDashboardScreen(),
        ),
        ShellTab(
          label: 'Batches',
          icon: Icons.inventory_2_outlined,
          child: FarmerHomeScreen(),
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
