import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/constants/constants.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int currentIndex = 0;

  final List<Map<String, String>> onboardingData = [
    {
      "image":
          "assets/images/onboarding_background.jpeg", // Plane facing forward
      "title": "Welcome to RVMS",
      "subtitle":
          "RVMS: Instant Decision, Confirmed SafetyAnalyze the runway and get the risk assessment in under 10 seconds. Save time and keep your focus sharp ",
    },
    {
      "image": "assets/images/onboarding_background.jpeg",
      "title": "Welcome to RVMS",
      "subtitle":
          "AI-Enhanced Accuracy, Automated Documentation\nScan, analyze, and let the AI pinpoint the hazard. Official PDF reports are automatically generated and sent for full compliance",
    },
    {
      "image": "assets/images/onboarding_background.jpeg",
      "title": "Welcome to RVMS",
      "subtitle":
          "Engineered for Critical Operations\nSimple interface, high contrast, and one single action button. Your decision is now faster and more accurate than ever",
    },
  ];

  void nextPage() {
    if (currentIndex < onboardingData.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      Navigator.pushReplacementNamed(context, kWelcomeScreen);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Background Image Slider
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            height: MediaQuery.of(context).size.height * 0.65,
            child: PageView.builder(
              controller: _pageController,
              itemCount: onboardingData.length,
              onPageChanged: (index) {
                setState(() {
                  currentIndex = index;
                });
              },
              itemBuilder: (context, index) {
                return Image.network(
                  onboardingData[index]["image"]!,
                  fit: BoxFit.cover,
                  alignment: Alignment.topCenter,
                  loadingBuilder: (context, child, loadingProgress) {
                    if (loadingProgress == null) return child;
                    return Container(
                      color: Colors.grey[200],
                      alignment: Alignment.center,
                      child: const CircularProgressIndicator(),
                    );
                  },
                );
              },
            ),
          ),

          // Bottom Content Card
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              height: MediaQuery.of(context).size.height * 0.42,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Color(0xFFF5F9FE),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 40, 24, 32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    //Title
                    Text(
                      onboardingData[currentIndex]["title"]!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1B233A),
                      ),
                    ),
                    const SizedBox(height: 16),

                    //subtitle
                    Text(
                      onboardingData[currentIndex]["subtitle"]!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xFF6C757D),
                        height: 1.5,
                      ),
                    ),
                    const Spacer(),

                    // Dots
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(
                        onboardingData.length,
                        (index) => AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          margin: const EdgeInsets.symmetric(horizontal: 5),
                          height: 8,
                          width: 8,
                          decoration: BoxDecoration(
                            color: currentIndex == index
                                ? const Color(0xFF1B233A)
                                : const Color(0xFFD6D9E0),
                            shape: BoxShape.circle,
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 32),

                    // Arrow Button
                    GestureDetector(
                      onTap: nextPage,
                      child: Container(
                        width: 56,
                        height: 56,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Color(0xFF0F1E3A),
                        ),
                        child: const Icon(
                          Icons.arrow_forward_rounded,
                          color: Colors.white,
                          size: 26,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
