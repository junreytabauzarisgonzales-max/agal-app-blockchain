import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:intl/intl.dart';
import 'package:uuid/uuid.dart';

import '../../core/auth/auth_controller.dart';
import '../../data/local/database.dart';
import '../../data/sync/sync_scheduler.dart';
import '../shared/agal_widgets.dart';
import '../shared/location_picker.dart';

class FarmerCreateBatchScreen extends StatefulWidget {
  const FarmerCreateBatchScreen({super.key});
  @override
  State<FarmerCreateBatchScreen> createState() =>
      _FarmerCreateBatchScreenState();
}

class _FarmerCreateBatchScreenState extends State<FarmerCreateBatchScreen> {
  final _formKey = GlobalKey<FormState>();
  final _weight = TextEditingController();
  String _species = 'Eucheuma Cottonii (Sakol)';
  DateTime _harvestedAt = DateTime.now();
  LatLng? _location;
  bool _saving = false;
  @override
  void dispose() {
    _weight.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final day = await showDatePicker(
      context: context,
      initialDate: _harvestedAt,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now(),
    );
    if (day == null || !mounted) return;
    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(_harvestedAt),
    );
    if (time != null && mounted)
      setState(
        () => _harvestedAt = DateTime(
          day.year,
          day.month,
          day.day,
          time.hour,
          time.minute,
        ),
      );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      final session = Get.find<AuthController>().session.value!;
      final weight = double.parse(_weight.text);
      await Get.find<AppDatabase>().insertBatchCreated(
        id: const Uuid().v4(),
        farmerId: session.userId,
        species: _species,
        estimatedWeightKg: weight,
        unit: 'kg',
        harvestedAt: _harvestedAt,
        harvestLatitude: _location?.latitude,
        harvestLongitude: _location?.longitude,
        payloadJson: jsonEncode({
          'species': _species,
          'estimated_weight_kg': weight,
          'unit': 'kg',
          'harvest_latitude': _location?.latitude,
          'harvest_longitude': _location?.longitude,
        }),
      );
      await Get.find<SyncScheduler>().refreshCounts();
      if (mounted) Get.back();
    } catch (_) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Could not save this harvest. Please try again.'),
          ),
        );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Log New Harvest')),
    body: ListView(
      padding: const EdgeInsets.all(18),
      children: [
        AgalSurface(
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionLabel('Select species'),
                RadioGroup<String>(
                  groupValue: _species,
                  onChanged: (v) => setState(() => _species = v!),
                  child: const Column(
                    children: [
                      RadioListTile<String>(
                        contentPadding: EdgeInsets.zero,
                        value: 'Eucheuma Cottonii (Sakol)',
                        title: Text(
                          'Eucheuma Cottonii (Sakol)',
                          style: TextStyle(fontSize: 13),
                        ),
                      ),
                      RadioListTile<String>(
                        contentPadding: EdgeInsets.zero,
                        value: 'Kappaphycus Alvarezii (Tambalang)',
                        title: Text(
                          'Kappaphycus Alvarezii (Tambalang)',
                          style: TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
                const SectionLabel('Estimated weight'),
                TextFormField(
                  controller: _weight,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    hintText: '180',
                    suffixText: 'kg',
                  ),
                  validator: (v) {
                    final n = double.tryParse(v ?? '');
                    return n == null || !n.isFinite || n <= 0
                        ? 'Enter a weight greater than zero'
                        : null;
                  },
                ),
                const SectionLabel('Harvest date & time'),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.schedule, size: 20),
                  title: Text(
                    DateFormat('MMM d, yyyy · h:mm a').format(_harvestedAt),
                    style: const TextStyle(fontSize: 13),
                  ),
                  trailing: const Icon(Icons.calendar_month_outlined),
                  onTap: _pickDate,
                ),
                const SectionLabel('GPS location'),
                LocationPicker(onChanged: (p) => _location = p),
                const SizedBox(height: 12),
                const Text(
                  'Saved securely on this device. Syncs when a connection is available.',
                  style: TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 18),
        FilledButton(
          onPressed: _saving ? null : _save,
          child: Text(_saving ? 'Saving…' : 'Save Harvest Batch'),
        ),
      ],
    ),
  );
}
