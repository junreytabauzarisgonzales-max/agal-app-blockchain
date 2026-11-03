import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

import '../../core/routes/app_routes.dart';
import '../../core/theme/app_theme.dart';
import '../../data/remote/agal_api_client.dart';
import '../shared/agal_widgets.dart';

class ChatListScreen extends StatefulWidget {
  const ChatListScreen({super.key});
  @override
  State<ChatListScreen> createState() => _ChatListScreenState();
}

class _ChatListScreenState extends State<ChatListScreen> {
  late Future<List<Map<String, dynamic>>> _future;
  int _filter = 0;
  String _search = '';
  @override
  void initState() {
    super.initState();
    _future = Get.find<AgalApiClient>().listThreads();
  }

  Future<void> _refresh() async {
    if (!mounted) return;
    setState(() { _future = Get.find<AgalApiClient>().listThreads(); });
    await _future;
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Messages'),
      actions: [
        IconButton(
          tooltip: 'New conversation',
          onPressed: () async {
            await Get.toNamed(Routes.chatContactPicker);
            if (mounted) _refresh();
          },
          icon: const Icon(Icons.edit_square),
        ),
      ],
    ),
    body: Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(18, 0, 18, 12),
          child: Column(
            children: [
              TextField(
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search, size: 20),
                  hintText: 'Search conversations',
                ),
                onChanged: (v) => setState(() => _search = v.toLowerCase()),
              ),
              const SizedBox(height: 12),
              FilterPills(
                labels: const ['All', 'Suppliers', 'Buyers', 'Farmers'],
                selected: _filter,
                onSelected: (v) => setState(() => _filter = v),
              ),
            ],
          ),
        ),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _refresh,
            child: FutureBuilder<List<Map<String, dynamic>>>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done)
                  return const Center(child: CircularProgressIndicator());
                if (snapshot.hasError)
                  return ListView(
                    children: const [
                      EmptyState(
                        icon: Icons.cloud_off_outlined,
                        title: 'You’re offline',
                        message: 'Open a saved conversation to queue messages, or pull down to retry when connected.',
                      ),
                    ],
                  );
                final threads = (snapshot.data ?? [])
                    .where(
                      (t) =>
                          (_filter == 0 ||
                              t['counterpart_role'] ==
                                  [
                                    '',
                                    'supplier',
                                    'buyer',
                                    'farmer',
                                  ][_filter]) &&
                          '${t['counterpart_name']}'.toLowerCase().contains(
                            _search,
                          ),
                    )
                    .toList();
                if (threads.isEmpty) {
                  return ListView(
                    children: const [
                      EmptyState(
                        icon: Icons.forum_outlined,
                        title: 'Start a conversation',
                        message: 'Tap the compose icon to connect with a farmer, supplier or buyer.',
                      ),
                    ],
                  );
                }
                return ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 18),
                  children: [
                    AgalSurface(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Column(
                        children: threads.map((t) {
                          final name = '${t['counterpart_name']}';
                          final unread = t['unread_count'] as int? ?? 0;
                          return ListTile(
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 14,
                              vertical: 5,
                            ),
                            leading: CircleAvatar(
                              backgroundColor: AgalColors.forest,
                              foregroundColor: AgalColors.mint,
                              child: Text(
                                name.isEmpty ? '?' : name[0].toUpperCase(),
                              ),
                            ),
                            title: Text(
                              name,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            subtitle: Text(
                              '${t['last_message_body']}',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                color: AgalColors.muted,
                                fontSize: 12,
                              ),
                            ),
                            trailing: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  DateFormat('MMM d').format(
                                    DateTime.parse('${t['last_message_at']}')
                                        .toLocal(),
                                  ),
                                  style: const TextStyle(
                                    color: AgalColors.muted,
                                    fontSize: 10,
                                  ),
                                ),
                                if (unread > 0) ...[
                                  const SizedBox(height: 6),
                                  CircleAvatar(
                                    radius: 10,
                                    backgroundColor: AgalColors.orange,
                                    child: Text(
                                      '$unread',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 11,
                                      ),
                                    ),
                                  ),
                                ],
                              ],
                            ),
                            onTap: () async {
                              await Get.toNamed(
                                Routes.chatThreadPath('${t['counterpart_id']}'),
                              );
                              if (mounted) _refresh();
                            },
                          );
                        }).toList(),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ),
      ],
    ),
  );
}
