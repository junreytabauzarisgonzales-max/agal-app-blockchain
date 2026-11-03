import 'dart:async';

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:uuid/uuid.dart';
import 'package:get_storage/get_storage.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';
import '../../data/local/database.dart';
import '../../data/remote/agal_api_client.dart';
import '../../data/sync/sync_scheduler.dart';
import '../../core/theme/app_theme.dart';
import '../shared/agal_widgets.dart';

class _ChatMessage {
  const _ChatMessage({
    required this.id,
    required this.body,
    required this.occurredAt,
    required this.isMine,
    required this.pending,
  });
  final String id;
  final String body;
  final DateTime occurredAt;
  final bool isMine;
  final bool pending;
}

class ChatThreadScreen extends StatefulWidget {
  const ChatThreadScreen({super.key, required this.counterpartId});
  final String counterpartId;

  @override
  State<ChatThreadScreen> createState() => _ChatThreadScreenState();
}

class _ChatThreadScreenState extends State<ChatThreadScreen> {
  final _textController = TextEditingController();
  List<Map<String, dynamic>> _serverMessages = [];
  Map<String, dynamic>? _counterpart;
  bool _loading = true;
  bool _sending = false;
  bool _offline = false;
  Timer? _pollTimer;

  late final String _myId;
  late final UserRole _myRole;

  @override
  void initState() {
    super.initState();
    final session = Get.find<AuthController>().session.value!;
    _myId = session.userId;
    _myRole = session.role;
    _counterpart = GetStorage().read<Map<String, dynamic>>(
      'contact_${session.userId}_${widget.counterpartId}',
    );
    _load();
    _pollTimer = Timer.periodic(const Duration(seconds: 15), (_) => _load());
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _textController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final api = Get.find<AgalApiClient>();
    try {
      final results = await Future.wait([
        api.getUser(widget.counterpartId),
        api.getConversation(widget.counterpartId),
      ]);
      unawaited(
        api.markConversationRead(widget.counterpartId).catchError((_) {}),
      );
      if (!mounted) return;
      setState(() {
        _counterpart = results[0] as Map<String, dynamic>;
        _serverMessages = results[1] as List<Map<String, dynamic>>;
        _loading = false;
        _offline = false;
      });
      await GetStorage().write(
        'contact_${_myId}_${widget.counterpartId}',
        _counterpart,
      );
    } catch (_) {
      if (mounted)
        setState(() {
          _loading = false;
          _offline = true;
        });
    }
  }

  Future<void> _send() async {
    final text = _textController.text.trim();
    if (text.isEmpty || _sending) return;
    setState(() => _sending = true);

    final id = const Uuid().v4();
    final now = DateTime.now();

    try {
      if (_myRole == UserRole.farmer) {
        await Get.find<AppDatabase>().insertOutgoingMessage(
          id: id,
          senderId: _myId,
          recipientId: widget.counterpartId,
          body: text,
          occurredAt: now,
        );
        await Get.find<SyncScheduler>().refreshCounts();
        unawaited(Get.find<SyncScheduler>().syncNow());
      } else {
        await Get.find<AgalApiClient>().sendMessage({
          'id': id,
          'recipient_id': widget.counterpartId,
          'body': text,
          'occurred_at': now.toUtc().toIso8601String(),
        });
        if (!mounted) return;
        setState(() {
          _serverMessages = [
            ..._serverMessages,
            {
              'id': id,
              'sender_id': _myId,
              'body': text,
              'occurred_at': now.toUtc().toIso8601String(),
            },
          ];
        });
      }
      _textController.clear();
    } catch (_) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Message could not be sent. Your draft is still here.',
            ),
          ),
        );
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  Future<void> _sendViaSms() async {
    final phone = _counterpart?['phone_number'] as String?;
    if (phone == null) return;
    final body = _textController.text.trim().isEmpty
        ? 'Hi, messaging you via Agal.'
        : _textController.text.trim();
    final uri = Uri(
      scheme: 'sms',
      path: phone,
      queryParameters: {'body': body},
    );
    try {
      if (!await launchUrl(uri)) throw Exception();
    } catch (_) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No SMS app is available on this device.'),
          ),
        );
    }
  }

  List<_ChatMessage> _merge(List<LocalMessage> local) {
    final byId = <String, _ChatMessage>{};
    for (final m in _serverMessages) {
      byId[m['id'] as String] = _ChatMessage(
        id: m['id'] as String,
        body: m['body'] as String,
        occurredAt: DateTime.parse(m['occurred_at'] as String).toLocal(),
        isMine: m['sender_id'] == _myId,
        pending: false,
      );
    }
    for (final m in local) {
      byId.putIfAbsent(
        m.id,
        () => _ChatMessage(
          id: m.id,
          body: m.body,
          occurredAt: m.occurredAt,
          isMine: true,
          pending: !m.synced,
        ),
      );
    }
    return byId.values.toList()
      ..sort((a, b) => a.occurredAt.compareTo(b.occurredAt));
  }

  @override
  Widget build(BuildContext context) {
    final phone = _counterpart?['phone_number'] as String?;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            CircleAvatar(
              radius: 17,
              backgroundColor: AgalColors.mint,
              child: Text(
                (_counterpart?['full_name'] as String? ?? '?').substring(0, 1),
                style: const TextStyle(color: AgalColors.deep),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                _counterpart?['full_name'] as String? ?? 'Chat',
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: phone == null
                ? 'No phone number on file'
                : 'Send via SMS instead',
            icon: const Icon(Icons.sms_outlined),
            onPressed: phone == null ? null : _sendViaSms,
          ),
        ],
      ),
      body: SafeArea(
        child: AgalSurface(
          padding: const EdgeInsets.all(8),
          child: Column(
            children: [
              if (_offline)
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFE4C5),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.cloud_off, size: 17, color: AgalColors.orange),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Offline · Farmer messages queue for sync',
                          style: TextStyle(color: AgalColors.ink, fontSize: 11),
                        ),
                      ),
                    ],
                  ),
                ),
              Expanded(
                child: _loading
                    ? const Center(child: CircularProgressIndicator())
                    : _myRole == UserRole.farmer
                    ? StreamBuilder<List<LocalMessage>>(
                        stream: Get.find<AppDatabase>().watchOutgoingMessagesTo(
                          widget.counterpartId,
                          _myId,
                        ),
                        builder: (context, snapshot) =>
                            _MessageList(messages: _merge(snapshot.data ?? [])),
                      )
                    : _MessageList(messages: _merge(const [])),
              ),
              if (phone != null)
                Align(
                  alignment: Alignment.centerRight,
                  child: Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: AgalColors.orange,
                        foregroundColor: Colors.white,
                      ),
                      onPressed: _sendViaSms,
                      icon: const Icon(Icons.sms_outlined, size: 17),
                      label: const Text('Send via SMS'),
                    ),
                  ),
                ),
              SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _textController,
                          minLines: 1,
                          maxLines: 4,
                          decoration: const InputDecoration(
                            hintText: 'Message',
                          ),
                          onSubmitted: (_) => _send(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton.filled(
                        onPressed: _sending ? null : _send,
                        icon: const Icon(Icons.send_rounded),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MessageList extends StatelessWidget {
  const _MessageList({required this.messages});
  final List<_ChatMessage> messages;

  @override
  Widget build(BuildContext context) {
    if (messages.isEmpty) {
      return const Center(child: Text('Say hello!'));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return Align(
          alignment: message.isMine
              ? Alignment.centerRight
              : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75,
            ),
            decoration: BoxDecoration(
              color: message.isMine ? AgalColors.mint : Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  message.body,
                  style: const TextStyle(color: AgalColors.ink, height: 1.4),
                ),
                const SizedBox(height: 2),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      DateFormat.Hm().format(message.occurredAt),
                      style: TextStyle(fontSize: 11, color: AgalColors.muted),
                    ),
                    if (message.pending) ...[
                      const SizedBox(width: 4),
                      Icon(
                        Icons.access_time,
                        size: 12,
                        color: AgalColors.muted,
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
