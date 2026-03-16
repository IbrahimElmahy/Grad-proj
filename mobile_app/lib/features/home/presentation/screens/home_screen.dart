import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: CircleAvatar(
          radius: 44,
          backgroundColor: Color(0xff020C1D),
          child: Image.asset(
            "assets/images/user_image.jpg",
            fit: BoxFit.fill,
            height: 500,
          ),
        ),

        title: Column(
          children: [
            Text(
              "hello, omar",
              style: TextStyle(
                color: Color(0xff000000),
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              "Safety officer",
              style: TextStyle(
                color: Color(0xff020C1D),
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
