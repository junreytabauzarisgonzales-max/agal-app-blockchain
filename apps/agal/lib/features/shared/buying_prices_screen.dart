import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

import '../../core/theme/app_theme.dart';
import '../../data/remote/agal_api_client.dart';
import 'agal_widgets.dart';

class BuyingPricesScreen extends StatefulWidget {
  const BuyingPricesScreen({super.key});
  @override
  State<BuyingPricesScreen> createState() => _BuyingPricesScreenState();
}

class _BuyingPricesScreenState extends State<BuyingPricesScreen> {
  late Future<List<Map<String, dynamic>>> _future;
  int _filter = 0;
  @override
  void initState() {
    super.initState();
    _future = Get.find<AgalApiClient>().listPrices();
  }

  Future<void> _refresh() async {
    setState(() { _future = Get.find<AgalApiClient>().listPrices(); });
    await _future;
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Today’s Buying Prices')),
    body: RefreshIndicator(
      onRefresh: _refresh,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            DateFormat('EEEE, MMMM d, yyyy').format(DateTime.now()),
            style: const TextStyle(color: Color(0xFFACC8BD), fontSize: 13),
          ),
          const SizedBox(height: 8),
          const Text(
            'Know your harvest’s value.',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          const Text(
            'Buying offers posted by Agal suppliers and buyers. Confirm the final price with your trading partner.',
            style: TextStyle(
              color: Color(0xFFACC8BD),
              fontSize: 13,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 18),
          FilterPills(
            labels: const ['All species', 'Cottonii', 'Tambalang'],
            selected: _filter,
            onSelected: (v) => setState(() => _filter = v),
          ),
          const SizedBox(height: 18),
          FutureBuilder<List<Map<String, dynamic>>>(
            future: _future,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done)
                return const Center(child: CircularProgressIndicator());
              if (snapshot.hasError)
                return const EmptyState(
                  icon: Icons.cloud_off_outlined,
                  title: 'Prices need a connection',
                  message: 'Harvests can still be logged offline. Pull down when connected to load the latest buying offers.',
                );
              final prices = (snapshot.data ?? [])
                  .where(
                    (p) =>
                        _filter == 0 ||
                        (_filter == 2) ==
                            (speciesLabel('${p['species']}') == 'Tambalang'),
                  )
                  .toList();
              if (prices.isEmpty)
                return const EmptyState(
                  icon: Icons.payments_outlined,
                  title: 'No offers posted yet',
                  message: 'Buying prices will appear here when your trading partners post them.',
                );
              final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
              return Column(
                children: prices
                    .map(
                      (p) => Padding(
                        padding: const EdgeInsets.only(bottom: 14),
                        child: AgalSurface(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  SeaweedArt(
                                    size: 60,
                                    tambalang:
                                        speciesLabel('${p['species']}') ==
                                        'Tambalang',
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          speciesLabel('${p['species']}'),
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w700,
                                            fontSize: 17,
                                          ),
                                        ),
                                        const SizedBox(height: 5),
                                        Text(
                                          '${p['grade'] ?? 'Ungraded'} · ${p['municipality'] ?? 'Tawi-Tawi'}',
                                          style: const TextStyle(
                                            color: AgalColors.muted,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 18),
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    '₱${NumberFormat('#,##0.00').format(double.tryParse('${p['price_per_kg']}') ?? 0)}',
                                    style: const TextStyle(
                                      fontSize: 34,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                  const Padding(
                                    padding: EdgeInsets.only(
                                      left: 5,
                                      bottom: 6,
                                    ),
                                    child: Text(
                                      '/ kg',
                                      style: TextStyle(color: AgalColors.muted),
                                    ),
                                  ),
                                  const Spacer(),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 10,
                                      vertical: 6,
                                    ),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFD1EBD8),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      '${p['effective_date']}' == today
                                          ? 'Posted today'
                                          : 'Latest offer',
                                      style: const TextStyle(
                                        fontSize: 10,
                                        color: AgalColors.forest,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Text(
                                'Effective ${p['effective_date']}',
                                style: const TextStyle(
                                  color: AgalColors.muted,
                                  fontSize: 11,
                                ),
                              ),
                              if ((p['notes'] as String? ?? '').isNotEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(top: 8),
                                  child: Text(
                                    '${p['notes']}',
                                    style: const TextStyle(fontSize: 12),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    )
                    .toList(),
              );
            },
          ),
        ],
      ),
    ),
  );
}
