import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/primary_button.dart';


class PasswordChangedScreen extends StatelessWidget {
  const PasswordChangedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false, 
         
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 48), // Push content down a bit
              
              // Icon Badge
              Center(
                child: Container(
                  width: 96,
                  height: 96,
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: const Color(0xFF3B82F6), // Light blue border a bit like the image
                      width: 1.5,
                    ),
                    // No explicit background color for the container so it's transparent inside the border apart from the icon
                  ),
                  child: const Center(
                    child: Icon(
                      Icons.verified, // Multi-pointed star badge with checkmark
                      color: Color(0xFF0F172A), // Dark blue like the badge in the image
                      size: 72,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Title
              const Text(
                "Successful",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B233A),
                ),
              ),
              const SizedBox(height: 16),

              // Subtitle
              const Text(
                "Congratulations! Your password has been\nchanged. Click continue to log in",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Color(0xFF6C757D),
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 48),

              // Continue Button
              PrimaryButton(
                text: "Continue",
                onPressed: () {
                  Navigator.pushNamedAndRemoveUntil(context, "/login", (route) => false);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
