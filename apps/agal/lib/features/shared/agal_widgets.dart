import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';

String batchLabel(String id) =>
    'BATCH #${id.replaceAll('-', '').substring(0, math.min(6, id.replaceAll('-', '').length)).toUpperCase()}';
String speciesLabel(String species) =>
    species.toLowerCase().contains('alvare') ||
        species.toLowerCase().contains('tambalang')
    ? 'Tambalang'
    : species.toLowerCase().contains('cotton') || species == 'Eucheuma'
    ? 'Cottonii (Sakol)'
    : species;

class AgalSurface extends StatelessWidget {
  const AgalSurface({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
  });
  final Widget child;
  final EdgeInsetsGeometry padding;
  @override
  Widget build(BuildContext context) {
    final light = ThemeData(useMaterial3: true, brightness: Brightness.light, fontFamily: 'Roboto');
    return Theme(
      data: light.copyWith(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF087960))
            .copyWith(surface: AgalColors.paper),
        scaffoldBackgroundColor: AgalColors.paper,
        textTheme: light.textTheme.apply(
          bodyColor: AgalColors.ink,
          displayColor: AgalColors.ink,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFFDDEEE5),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 15,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
        ),
        filledButtonTheme: Theme.of(context).filledButtonTheme,
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(foregroundColor: AgalColors.forest),
        ),
      ),
      child: DefaultTextStyle(
        style: const TextStyle(color: AgalColors.ink, fontSize: 14, fontFamily: 'Roboto'),
        child: Material(color: AgalColors.paper, borderRadius: BorderRadius.circular(20),
          child: SizedBox(width: double.infinity, child: Padding(padding: padding, child: child))),
      ),
    );
  }
}

class SectionLabel extends StatelessWidget {
  const SectionLabel(this.text, {super.key});
  final String text;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(top: 18, bottom: 10),
    child: Text(
      text,
      style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
    ),
  );
}

class FilterPills extends StatelessWidget {
  const FilterPills({
    super.key,
    required this.labels,
    required this.selected,
    required this.onSelected,
  });
  final List<String> labels;
  final int selected;
  final ValueChanged<int> onSelected;
  @override
  Widget build(BuildContext context) => SingleChildScrollView(
    scrollDirection: Axis.horizontal,
    child: Row(
      children: List.generate(
        labels.length,
        (i) => Padding(
          padding: const EdgeInsets.only(right: 8),
          child: ChoiceChip(
            label: Text(labels[i]),
            selected: selected == i,
            onSelected: (_) => onSelected(i),
            showCheckmark: false,
            selectedColor: AgalColors.mint,
            backgroundColor: const Color(0xFF16493E),
            labelStyle: TextStyle(
              color: selected == i ? AgalColors.deep : Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    ),
  );
}

class BatchProgress extends StatelessWidget {
  const BatchProgress({super.key, required this.status});
  final String status;
  @override
  Widget build(BuildContext context) {
    final stage = switch (status) {
      'drying' => 1,
      'dried' => 2,
      'with_supplier' || 'with_buyer' || 'exported' => 3,
      _ => 0,
    };
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: List.generate(
          4,
          (i) => Expanded(
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Container(
                        height: 2,
                        color: i == 0
                            ? Colors.transparent
                            : i <= stage
                            ? const Color(0xFF36A586)
                            : const Color(0xFFCADBD3),
                      ),
                    ),
                    Icon(
                      i < stage
                          ? Icons.check_circle
                          : i == stage
                          ? Icons.radio_button_checked
                          : Icons.radio_button_unchecked,
                      size: 23,
                      color: i <= stage
                          ? AgalColors.forest
                          : const Color(0xFFBDCEC5),
                    ),
                    Expanded(
                      child: Container(
                        height: 2,
                        color: i == 3
                            ? Colors.transparent
                            : i < stage
                            ? const Color(0xFF36A586)
                            : const Color(0xFFCADBD3),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 7),
                Text(
                  ['Harvested', 'Drying', 'Ready for\npickup', 'Handed off'][i],
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 10, color: AgalColors.ink),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class SeaweedArt extends StatelessWidget {
  const SeaweedArt({super.key, this.size = 74, this.tambalang = false});
  final double size;
  final bool tambalang;
  @override
  Widget build(BuildContext context) => Container(
    width: size,
    height: size,
    decoration: BoxDecoration(
      color: tambalang ? const Color(0xFFE6DCD0) : const Color(0xFFD8E7D5),
      borderRadius: BorderRadius.circular(14),
    ),
    child: CustomPaint(painter: _SeaweedPainter(tambalang)),
  );
}

class _SeaweedPainter extends CustomPainter {
  _SeaweedPainter(this.brown);
  final bool brown;
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = brown ? const Color(0xFF8D5D43) : const Color(0xFF648049)
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 2.5;
    final random = math.Random(7);
    void branch(Offset origin, double length, double angle, int depth) {
      if (depth == 0) return;
      final end =
          origin + Offset(math.cos(angle) * length, math.sin(angle) * length);
      canvas.drawLine(origin, end, paint);
      branch(
        end,
        length * .7,
        angle - .48 - random.nextDouble() * .25,
        depth - 1,
      );
      branch(
        end,
        length * .72,
        angle + .48 + random.nextDouble() * .25,
        depth - 1,
      );
    }

    for (var i = 0; i < 5; i++) {
      branch(
        Offset(size.width * .5, size.height * .86),
        size.height * .23,
        -math.pi / 2 + (i - 2) * .24,
        4,
      );
    }
  }

  @override
  bool shouldRepaint(_SeaweedPainter oldDelegate) => oldDelegate.brown != brown;
}

class EmptyState extends StatelessWidget {
  const EmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
  });
  final IconData icon;
  final String title, message;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 24),
    child: Column(
      children: [
        Icon(icon, size: 48, color: AgalColors.mint),
        const SizedBox(height: 16),
        Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 18),
        ),
        const SizedBox(height: 8),
        Text(
          message,
          textAlign: TextAlign.center,
          style: const TextStyle(color: Color(0xFFACC8BD), height: 1.5),
        ),
      ],
    ),
  );
}
