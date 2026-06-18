import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';

class DraggableCheckBar extends StatefulWidget {
  const DraggableCheckBar({
    super.key,
    required this.onCompleted,
  });

  final VoidCallback onCompleted;

  @override
  State<DraggableCheckBar> createState() => _DraggableCheckBarState();
}

class _DraggableCheckBarState extends State<DraggableCheckBar>
    with SingleTickerProviderStateMixin {
  double _dragPosition = 0;
  bool _isCompleted = false;
  late AnimationController _glowController;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _glowController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _glowAnimation = Tween<double>(begin: 3.0, end: 12.0).animate(
      CurvedAnimation(parent: _glowController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        const double knobSize = 52;
        final double maxDrag = constraints.maxWidth - knobSize - 8;
        final double progress = maxDrag > 0 ? (_dragPosition / maxDrag) : 0.0;

        return AnimatedBuilder(
          animation: _glowAnimation,
          builder: (context, child) {
            return Container(
              height: 60,
              padding: const EdgeInsets.symmetric(horizontal: 4),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(30),
                border: Border.all(
                  color: AppColors.primary.withOpacity(0.4),
                  width: 1.5,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.2),
                    blurRadius: _glowAnimation.value,
                    spreadRadius: _glowAnimation.value * 0.1,
                  ),
                ],
              ),
              child: child,
            );
          },
          child: Stack(
            alignment: Alignment.centerLeft,
            children: [
              Positioned.fill(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(30),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      Image.asset(
                        'assets/images/drag_check_bg.jpg',
                        fit: BoxFit.cover,
                      ),
                      Container(
                        color: Colors.black.withOpacity(.12),
                      ),
                    ],
                  ),
                ),
              ),
              const Center(
                child: Text(
                  'Drag For New Check',
                  style: TextStyle(
                    fontSize: 15,
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Positioned(
                left: _dragPosition,
                child: GestureDetector(
                  onHorizontalDragUpdate: (details) {
                    if (_isCompleted) return;

                    setState(() {
                      _dragPosition += details.delta.dx;
                      if (_dragPosition < 0) _dragPosition = 0;
                      if (_dragPosition > maxDrag) _dragPosition = maxDrag;
                    });
                  },
                  onHorizontalDragEnd: (_) {
                    if (_dragPosition >= maxDrag * 0.85) {
                      setState(() {
                        _dragPosition = maxDrag;
                        _isCompleted = true;
                      });
                      widget.onCompleted();
                      Future.delayed(const Duration(milliseconds: 600), () {
                        if (mounted) {
                          setState(() {
                            _dragPosition = 0;
                            _isCompleted = false;
                          });
                        }
                      });
                    } else {
                      setState(() {
                        _dragPosition = 0;
                      });
                    }
                  },
                  child: Container(
                    width: knobSize,
                    height: knobSize,
                    decoration: const BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                    ),
                    child: Transform.rotate(
                      angle: -progress * 0.5,
                      child: const Icon(
                        Icons.flight,
                        color: Colors.white,
                        size: 24,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}


