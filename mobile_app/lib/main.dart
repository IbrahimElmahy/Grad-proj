import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:gradiuationg_project/core/constants/constants.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/create_password_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/enter_code_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/forgot_password_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/password_changed_screen.dart';
import 'package:gradiuationg_project/features/auth/presentation/screens/welcome_screen.dart';
import 'package:gradiuationg_project/features/home/presentation/screens/home_screen.dart';
import 'package:gradiuationg_project/features/onboarding/presentation/screens/onboarding_screen.dart';
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
      initialRoute: "/",
      routes: {
        "/": (context) => const SplashScreen(),
        kOnboardingScreen: (context) => const OnboardingScreen(),
        kWelcomeScreen: (context) => const WelcomeScreen(),
        kLoginScreen: (context) => const LoginScreen(),
        kForgetPasswordScreen: (context) => const ForgotPasswordScreen(),
        kEnterCodeScreen: (context) => const EnterCodeScreen(),
        kCreatePasswordScreen: (context) => const CreatePasswordScreen(),
        kPasswordChangedScreen: (context) => const PasswordChangedScreen(),
        kHomeScreen: (context) => const HomeScreen(),
      },
    );
  }
}
