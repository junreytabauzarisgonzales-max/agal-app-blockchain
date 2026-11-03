import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../data/remote/agal_api_client.dart';

class ShellTab {
  const ShellTab({
    required this.label,
    required this.icon,
    required this.child,
    this.showBadge = false,
  });
  final String label;
  final IconData icon;
  final Widget child;

  /// Only the Messages tab sets this -- see [_TabIcon].
  final bool showBadge;
}

/// Hosts a role's tabs behind a persistent bottom nav bar. Each tab widget
/// keeps its own Scaffold/AppBar; this just swaps which one is visible
/// (via IndexedStack, so switching tabs doesn't lose scroll position or
/// re-fetch data) and supplies the NavigationBar underneath all of them.
class RoleShell extends StatefulWidget {
  const RoleShell({super.key, required this.tabs});
  final List<ShellTab> tabs;

  @override
  State<RoleShell> createState() => _RoleShellState();
}

class _RoleShellState extends State<RoleShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _index,
        children: widget.tabs.map((t) => t.child).toList(),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (index) => setState(() => _index = index),
        destinations: [
          for (final tab in widget.tabs)
            NavigationDestination(
              icon: tab.showBadge
                  ? _BadgedIcon(icon: tab.icon)
                  : Icon(tab.icon),
              label: tab.label,
            ),
        ],
      ),
    );
  }
}

/// Live unread-message count on the Messages tab's icon. Fetched once per
/// shell mount and refreshed whenever the tab becomes selected again would
/// be nicer, but a single fetch on shell startup keeps this simple --
/// good enough for a badge that's a hint, not a source of truth.
class _BadgedIcon extends StatefulWidget {
  const _BadgedIcon({required this.icon});
  final IconData icon;

  @override
  State<_BadgedIcon> createState() => _BadgedIconState();
}

class _BadgedIconState extends State<_BadgedIcon> {
  int _unread = 0;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    try {
      final threads = await Get.find<AgalApiClient>().listThreads();
      final total = threads.fold<int>(
        0,
        (sum, t) => sum + (t['unread_count'] as int),
      );
      if (mounted) setState(() => _unread = total);
    } catch (_) {
      // Offline or not yet reachable -- just show no badge.
    }
  }

  @override
  Widget build(BuildContext context) {
    return Badge(
      isLabelVisible: _unread > 0,
      label: Text('$_unread'),
      child: Icon(widget.icon),
    );
  }
}
