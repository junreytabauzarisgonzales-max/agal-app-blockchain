import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/routes/app_routes.dart';
import '../../data/remote/agal_api_client.dart';

class ContactPickerScreen extends StatefulWidget {
  const ContactPickerScreen({super.key});

  @override
  State<ContactPickerScreen> createState() => _ContactPickerScreenState();
}

class _ContactPickerScreenState extends State<ContactPickerScreen> {
  late Future<List<Map<String, dynamic>>> _directoryFuture;

  @override
  void initState() {
    super.initState();
    _directoryFuture = Get.find<AgalApiClient>().listDirectory();
  }

  @override
  Widget build(BuildContext context) {
    final myId = Get.find<AuthController>().session.value!.userId;

    return Scaffold(
      appBar: AppBar(title: const Text('New message')),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _directoryFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return const Center(
              child: Text('Could not load contacts. Check your connection.'),
            );
          }
          final contacts = (snapshot.data ?? [])
              .where((u) => u['id'] != myId)
              .toList();
          if (contacts.isEmpty) {
            return const Center(child: Text('No one else has registered yet.'));
          }
          return ListView.separated(
            itemCount: contacts.length,
            separatorBuilder: (_, _) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final user = contacts[index];
              return ListTile(
                leading: CircleAvatar(
                  child: Text((user['full_name'] as String)[0].toUpperCase()),
                ),
                title: Text(user['full_name'] as String),
                subtitle: Text(_roleLabel(user['role'] as String)),
                onTap: () =>
                    Get.offNamed(Routes.chatThreadPath(user['id'] as String)),
              );
            },
          );
        },
      ),
    );
  }

  String _roleLabel(String value) => switch (value) {
    'farmer' => 'Farmer',
    'supplier' => 'Supplier / Aggregator',
    'buyer' => 'Buyer / Exporter',
    _ => value,
  };
}
