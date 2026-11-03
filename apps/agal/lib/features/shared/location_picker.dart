import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/theme/app_theme.dart';

class LocationPicker extends StatefulWidget {
  const LocationPicker({super.key, required this.onChanged});
  final ValueChanged<LatLng?> onChanged;
  @override
  State<LocationPicker> createState() => _LocationPickerState();
}

class _LocationPickerState extends State<LocationPicker> {
  LatLng? _position;
  bool _loading = false;
  String? _error;
  Future<void> _locate() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      if (!await Geolocator.isLocationServiceEnabled())
        throw Exception('Turn on location services and try again.');
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied)
        permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.deniedForever ||
          permission == LocationPermission.denied) {
        throw Exception('Allow location permission to tag your harvest.');
      }
      final p = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 20),
        ),
      );
      if (!mounted) return;
      setState(() => _position = LatLng(p.latitude, p.longitude));
      widget.onChanged(_position);
    } catch (e) {
      if (mounted)
        setState(() => _error = '$e'.replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      if (_position != null) ...[
        Text(
          '${_position!.latitude.toStringAsFixed(6)}, ${_position!.longitude.toStringAsFixed(6)}',
          style: const TextStyle(fontSize: 12),
        ),
        const SizedBox(height: 10),
        MapPreview(
          latitude: _position!.latitude,
          longitude: _position!.longitude,
        ),
      ] else
        Container(
          height: 140,
          decoration: BoxDecoration(
            color: const Color(0xFFDDEADB),
            borderRadius: BorderRadius.circular(14),
          ),
          child: const Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.location_on, color: Color(0xFF168B75), size: 36),
              SizedBox(height: 8),
              Text(
                'Tag this harvest with your GPS location',
                style: TextStyle(fontSize: 12, color: AgalColors.muted),
              ),
            ],
          ),
        ),
      const SizedBox(height: 10),
      FilledButton.icon(
        onPressed: _loading ? null : _locate,
        icon: Icon(
          _loading ? Icons.hourglass_top : Icons.my_location,
          size: 18,
        ),
        label: Text(_loading ? 'Getting location…' : 'Use Current Location'),
      ),
      if (_error != null)
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Text(
            _error!,
            style: const TextStyle(fontSize: 12, color: Colors.red),
          ),
        ),
    ],
  );
}

class MapPreview extends StatelessWidget {
  const MapPreview({
    super.key,
    required this.latitude,
    required this.longitude,
  });
  final double latitude, longitude;
  @override
  Widget build(BuildContext context) {
    const tiles = 16384;
    final x = (longitude + 180) / 360 * tiles;
    final radians = latitude.clamp(-85.05, 85.05) * math.pi / 180;
    final y =
        (1 - math.log(math.tan(radians) + 1 / math.cos(radians)) / math.pi) /
        2 *
        tiles;
    return ClipRRect(
      borderRadius: BorderRadius.circular(14),
      child: SizedBox(
        height: 165,
        child: Stack(
          fit: StackFit.expand,
          children: [
            Image.network(
              'https://tile.openstreetmap.org/14/${x.floor()}/${y.floor()}.png',
              fit: BoxFit.fill,
              headers: const {
                'User-Agent': 'Agal/1.0 (seaweed traceability app)',
              },
              errorBuilder: (_, _, _) => Container(
                color: const Color(0xFFDDEADB),
                child: const Center(
                  child: Text(
                    'Map unavailable offline · GPS saved',
                    style: TextStyle(color: AgalColors.muted, fontSize: 12),
                  ),
                ),
              ),
            ),
            Align(
              alignment: Alignment(
                (x - x.floor()) * 2 - 1,
                (y - y.floor()) * 2 - 1,
              ),
              child: const Icon(
                Icons.location_on,
                color: Color(0xFF078F7C),
                size: 34,
              ),
            ),
            Positioned(
              bottom: 4,
              right: 5,
              child: InkWell(
                onTap: () => launchUrl(
                  Uri.parse(
                    'https://www.openstreetmap.org/?mlat=$latitude&mlon=$longitude#map=14/$latitude/$longitude',
                  ),
                ),
                child: Container(
                  color: Colors.white.withValues(alpha: .9),
                  padding: const EdgeInsets.all(3),
                  child: const Text(
                    '© OpenStreetMap contributors',
                    style: TextStyle(color: AgalColors.ink, fontSize: 9),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
