// import 'dart:ui';

// import 'package:flutter/material.dart';

// class ReportTypeButton extends StatelessWidget {
//   final String title;
//   final bool isSelected;

//   const ReportTypeButton({super.key, 
//     required this.title,
//     required this.isSelected,
//   });

//   @override
//   Widget build(BuildContext context) {
//     final Color backgroundColor =
//         isSelected ? const Color(0xff001B3F) : Colors.transparent;

//     final Color contentColor =
//         isSelected ? Colors.white : const Color(0xff001B3F);

//     return Container(
//       height: 36,
//       decoration: BoxDecoration(
//         color: backgroundColor,
//         borderRadius: BorderRadius.circular(9),
//         border: Border.all(
//           color: const Color(0xff001B3F),
//           width: 0.8,
//         ),
//       ),
//       child: Row(
//         mainAxisAlignment: MainAxisAlignment.center,
//         children: [
//           Icon(
//             Icons.article_outlined,
//             size: 18,
//             color: contentColor,
//           ),
//           const SizedBox(width: 10),
//           Text(
//             title,
//             style: TextStyle(
//               fontSize: 14,
//               fontWeight: FontWeight.w500,
//               color: contentColor,
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }