import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/routes/app_routes.dart';
import '../../core/theme/app_theme.dart';
import '../../data/remote/agal_api_client.dart';
import 'agal_widgets.dart';

class SourcingScreen extends StatefulWidget {
  const SourcingScreen({super.key, required this.supplier});
  final bool supplier;
  @override
  State<SourcingScreen> createState() => _SourcingScreenState();
}

class _SourcingScreenState extends State<SourcingScreen> {
  late Future<void> _future;
  List<Map<String, dynamic>> _batches = [];
  Map<String, Map<String, dynamic>> _people = {};
  String _query = '';
  int _filter = 0;
  Position? _position;
  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<void> _load() async {
    final api = Get.find<AgalApiClient>();
    final results = await Future.wait([api.listBatches(), api.listDirectory()]);
    _batches = results[0];
    _people = {for (final p in results[1]) p['id'] as String: p};
  }

  Future<void> _refresh() async {
    setState(() { _future = _load(); });
    await _future;
  }

  double? _distance(Map<String, dynamic> batch) {
    final lat = double.tryParse('${batch['harvest_latitude']}');
    final lng = double.tryParse('${batch['harvest_longitude']}');
    return _position == null || lat == null || lng == null
        ? null
        : Geolocator.distanceBetween(
                _position!.latitude,
                _position!.longitude,
                lat,
                lng,
              ) /
              1000;
  }

  Future<void> _nearby() async {
    try {
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied)
        permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever)
        throw Exception();
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          timeLimit: Duration(seconds: 15),
        ),
      );
      if (mounted) setState(() => _position = position);
    } catch (_) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Enable location to sort batches nearest to you.'),
          ),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final filters = widget.supplier
        ? ['Ready for pickup', 'My inventory', 'Nearby', 'All']
        : ['All', 'Cottonii', 'Tambalang', 'Nearby', 'My purchases'];
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.supplier ? 'Pickup Dashboard' : 'Sourcing Marketplace',
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 2, 18, 12),
            child: Column(
              children: [
                TextField(
                  onChanged: (v) => setState(() => _query = v.toLowerCase()),
                  decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.search, size: 21),
                    hintText: widget.supplier
                        ? 'Search farmer, batch or location'
                        : 'Search species, location or supplier',
                    hintStyle: const TextStyle(fontSize: 12),
                  ),
                ),
                const SizedBox(height: 12),
                FilterPills(
                  labels: filters,
                  selected: _filter,
                  onSelected: (i) {
                    setState(() => _filter = i);
                    if (filters[i] == 'Nearby') _nearby();
                  },
                ),
              ],
            ),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: _refresh,
              child: FutureBuilder<void>(
                future: _future,
                builder: (context, snapshot) {
                  if (snapshot.connectionState != ConnectionState.done)
                    return const Center(child: CircularProgressIndicator());
                  if (snapshot.hasError) {
                    return ListView(
                      children: [
                        const EmptyState(
                          icon: Icons.cloud_off_outlined,
                          title: 'Could not load batches',
                          message: 'Check your connection, then pull down to try again.',
                        ),
                        Center(
                          child: TextButton(
                            onPressed: _refresh,
                            child: const Text('Try again'),
                          ),
                        ),
                      ],
                    );
                  }
                  final myId = Get.find<AuthController>().session.value!.userId;
                  final label = filters[_filter];
                  final shown = _batches.where((b) {
                    final status = b['status'];
                    if (widget.supplier) {
                      if (label == 'My inventory' &&
                          !(b['current_holder_id'] == myId &&
                              status == 'with_supplier'))
                        return false;
                      if (label != 'My inventory' &&
                          label != 'All' &&
                          status != 'dried')
                        return false;
                      if (label == 'All' &&
                          status != 'dried' &&
                          b['current_holder_id'] != myId)
                        return false;
                    } else {
                      if (label == 'My purchases'
                          ? !(b['current_holder_id'] == myId &&
                                status == 'with_buyer')
                          : status != 'with_supplier')
                        return false;
                      if (label == 'Cottonii' &&
                          speciesLabel('${b['species']}') == 'Tambalang')
                        return false;
                      if (label == 'Tambalang' &&
                          speciesLabel('${b['species']}') != 'Tambalang')
                        return false;
                    }
                    final owner =
                        _people[widget.supplier
                            ? b['farmer_id']
                            : b['current_holder_id']];
                    return '${b['id']} ${b['species']} ${owner?['full_name']} ${owner?['municipality']}'
                        .toLowerCase()
                        .contains(_query);
                  }).toList();
                  if (label == 'Nearby' && _position != null)
                    shown.sort(
                      (a, b) => (_distance(a) ?? double.infinity).compareTo(
                        _distance(b) ?? double.infinity,
                      ),
                    );
                  if (shown.isEmpty) {
                    return ListView(
                      children: const [
                        EmptyState(
                          icon: Icons.grass_outlined,
                          title: 'No batches here yet',
                          message: 'Try another filter or check back after new harvests are synced.',
                        ),
                      ],
                    );
                  }
                  return ListView.separated(
                    padding: const EdgeInsets.fromLTRB(18, 0, 18, 20),
                    itemCount: shown.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 12),
                    itemBuilder: (context, i) {
                      final b = shown[i];
                      final owner =
                          _people[widget.supplier
                              ? b['farmer_id']
                              : b['current_holder_id']];
                      final canReceive = widget.supplier
                          ? b['status'] == 'dried'
                          : b['status'] == 'with_supplier';
                      final distance = _distance(b);
                      return AgalSurface(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          children: [
                            InkWell(
                              onTap: () => Get.toNamed(
                                Routes.batchHistoryPath(b['id'] as String),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  SeaweedArt(
                                    size: 84,
                                    tambalang:
                                        speciesLabel('${b['species']}') ==
                                        'Tambalang',
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          widget.supplier
                                              ? batchLabel('${b['id']}')
                                              : speciesLabel('${b['species']}'),
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w800,
                                            fontSize: 15,
                                          ),
                                        ),
                                        const SizedBox(height: 5),
                                        Text(
                                          '${b['estimated_weight_kg']} ${b['unit']}',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        const SizedBox(height: 5),
                                        Text(
                                          owner?['full_name'] as String? ??
                                              'Seaweed partner',
                                          style: const TextStyle(fontSize: 12),
                                        ),
                                        if (widget.supplier)
                                          Text(
                                            speciesLabel('${b['species']}'),
                                            style: const TextStyle(
                                              fontSize: 12,
                                            ),
                                          ),
                                        const SizedBox(height: 6),
                                        Text(
                                          '⌖ ${owner?['municipality'] ?? 'Location not provided'}${distance == null ? '' : ' · ${distance.toStringAsFixed(1)} km'}',
                                          style: const TextStyle(
                                            color: AgalColors.muted,
                                            fontSize: 11,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Flexible(child: Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 9,
                                    vertical: 5,
                                  ),
                                  decoration: BoxDecoration(
                                    color: canReceive && widget.supplier
                                        ? const Color(0xFFFFDBAF)
                                        : const Color(0xFFCBEDCC),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    canReceive && widget.supplier
                                        ? 'Ready for Pickup'
                                        : canReceive
                                        ? 'Available for sourcing'
                                        : 'In your inventory',
                                    style: const TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                )),
                                const SizedBox(width: 6),
                                if (canReceive)
                                  TextButton(
                                    onPressed: () async {
                                      await Get.toNamed(
                                        Routes.verifyHandoverPath(
                                          b['id'] as String,
                                        ),
                                      );
                                      if (mounted) _refresh();
                                    },
                                    child: Text(
                                      widget.supplier
                                          ? 'Verify & receive'
                                          : 'View & purchase',
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                  )
                                else
                                  IconButton(
                                    tooltip: 'View provenance',
                                    onPressed: () => Get.toNamed(
                                      Routes.batchHistoryPath('${b['id']}'),
                                    ),
                                    icon: const Icon(Icons.chevron_right),
                                  ),
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
