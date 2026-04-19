import 'package:flutter/material.dart';

abstract class AppColors {
  static const Color primary = Color(0xff062B6F);
  static const Color background = Color(0xffF5F7FB);
  static const Color softCard = Color(0xffE8EEF8);
  static const Color textDark = Color(0xff111111);
  static const Color textGrey = Color(0xff666666);
  static const Color border = Color(0xffD3DAE6);

  static const Color safe = Color(0xff58F25B);
  static const Color medium = Color(0xffFFD54F);
  static const Color highRisk = Color(0xffF6A63A);

  static const LinearGradient navIconGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [
      Color(0xFF03183A),
      Color(0xFF022257),
      Color(0xFF012664),
      Color(0xFF022C74),
      Color(0xFF022B71),
    ],
  );
}