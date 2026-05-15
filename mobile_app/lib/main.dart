import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:gradiuationg_project/core/constants/constants.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/create_password_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/enter_code_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/forgot_password_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/password_changed_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/welcome_screen.dart';
import 'package:gradiuationg_project/features/alerts/presentation/screens/alerts_screen.dart';
import 'package:gradiuationg_project/features/history/presentation/screens/history_screen.dart';
import 'package:gradiuationg_project/features/home/presentation/screens/home_screen.dart';
import 'package:gradiuationg_project/features/inspections/presentation/screens/inspection_detail_screen.dart';
import 'package:gradiuationg_project/features/onboarding/presentation/screens/onboarding_screen.dart';
import 'package:gradiuationg_project/features/settings/presentation/screens/account_info_screen.dart';
import 'package:gradiuationg_project/features/settings/presentation/screens/notifications_screen.dart';
import 'package:gradiuationg_project/features/settings/presentation/screens/privacy_screen.dart';
import 'package:gradiuationg_project/features/settings/presentation/screens/settings_screen.dart';
import 'package:gradiuationg_project/features/splash/presentation/screens/splash_screen.dart';

import 'features/auth/presentation/screens/login_screen.dart' show LoginScreen;

void main() {
  runApp(const RVMS());
}

class RVMS extends StatelessWidget {
  const RVMS({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        textTheme: GoogleFonts.poppinsTextTheme(),
        primaryTextTheme: GoogleFonts.poppinsTextTheme(),
        appBarTheme: AppBarTheme(
          titleTextStyle: GoogleFonts.poppins(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
      ),
      initialRoute: AppRoutes.splash,
      routes: {
        AppRoutes.splash: (context) => const SplashScreen(),
        AppRoutes.onboarding: (context) => const OnboardingScreen(),
        AppRoutes.welcome: (context) => const WelcomeScreen(),
        AppRoutes.login: (context) => const LoginScreen(),
        AppRoutes.forgotPassword: (context) => const ForgotPasswordScreen(),
        AppRoutes.enterCode: (context) => const EnterCodeScreen(),
        AppRoutes.createPassword: (context) => const CreatePasswordScreen(),
        AppRoutes.passwordChanged: (context) => const PasswordChangedScreen(),
        AppRoutes.home: (context) => const HomeScreen(),
        AppRoutes.history: (context) => const HistoryScreen(),
        AppRoutes.alerts: (context) => const AlertsScreen(),
        AppRoutes.inspectionDetail: (context) => const InspectionDetailScreen(),
        AppRoutes.settings: (context) => const SettingsScreen(),
        AppRoutes.accountInfo: (context) => const AccountInfoScreen(),
        AppRoutes.notifications: (context) => const NotificationsScreen(),
        AppRoutes.privacy: (context) => const PrivacyScreen(),
        AppRoutes.about: (context) => const AboutScreen(),
      },
    );
  }
}
