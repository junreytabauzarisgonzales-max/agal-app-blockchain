import 'package:flutter/material.dart';

class AgalColors {
  static const forest = Color(0xFF002D26);
  static const deep = Color(0xFF001F1B);
  static const mint = Color(0xFF83F5CE);
  static const paper = Color(0xFFEDF7F1);
  static const ink = Color(0xFF102D29);
  static const muted = Color(0xFF647C73);
  static const orange = Color(0xFFEF790F);
}

class AppTheme {
  AppTheme._();
  static final light = _build(Brightness.light);
  static final dark = _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final scheme =
        ColorScheme.fromSeed(
          seedColor: AgalColors.mint,
          brightness: brightness,
        ).copyWith(
          primary: AgalColors.mint,
          onPrimary: AgalColors.deep,
          surface: AgalColors.forest,
          onSurface: Colors.white,
          onSurfaceVariant: const Color(0xFFACC8BD),
        );
    return ThemeData(
      fontFamily: 'Roboto',
      useMaterial3: true,
      brightness: brightness,
      colorScheme: scheme,
      scaffoldBackgroundColor: AgalColors.deep,
      textTheme: ThemeData.dark().textTheme.apply(
        fontFamily: 'Roboto',
        bodyColor: Colors.white,
        displayColor: Colors.white,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AgalColors.deep,
        foregroundColor: Colors.white,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontFamily: 'Roboto',
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
      cardTheme: CardThemeData(
        color: AgalColors.forest,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFF174D43),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 17,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: AgalColors.mint,
          foregroundColor: AgalColors.deep,
          minimumSize: const Size(0, 50),
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 15),
          textStyle: const TextStyle(fontFamily: 'Roboto', fontWeight: FontWeight.w700, fontSize: 14),
          shape: const StadiumBorder(),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AgalColors.mint,
          side: const BorderSide(color: AgalColors.mint),
          minimumSize: const Size(0, 46),
          shape: const StadiumBorder(),
        ),
      ),
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: AgalColors.mint,
        foregroundColor: AgalColors.deep,
      ),
      navigationBarTheme: NavigationBarThemeData(
        height: 74,
        backgroundColor: AgalColors.deep,
        indicatorColor: AgalColors.mint.withValues(alpha: .12),
        iconTheme: WidgetStateProperty.resolveWith(
          (s) => IconThemeData(
            color: s.contains(WidgetState.selected)
                ? AgalColors.mint
                : const Color(0xFF88A89D),
          ),
        ),
        labelTextStyle: WidgetStateProperty.resolveWith(
          (s) => TextStyle(
            fontSize: 11,
            color: s.contains(WidgetState.selected)
                ? AgalColors.mint
                : const Color(0xFF88A89D),
          ),
        ),
      ),
      chipTheme: const ChipThemeData(
        side: BorderSide.none,
        shape: StadiumBorder(),
      ),
      dividerTheme: const DividerThemeData(
        color: Color(0xFF285247),
        thickness: .6,
      ),
      snackBarTheme: const SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
