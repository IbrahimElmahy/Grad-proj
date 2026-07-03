import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/constants/constants.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';
import 'package:gradiuationg_project/features/auth/data/auth_session.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../inspections/data/inspection_service.dart';
import '../../../inspections/data/models/inspection_model.dart';
import '../../data/models/alert_model.dart';
import '../widgets/alert_card.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  final InspectionService _inspectionService = const InspectionService();
  bool _isLoading = true;
  String _errorMessage = '';
  List<AlertModel> _activeAlerts = [];
  final Set<String> _resolvedAlertIds = {};

  @override
  void initState() {
    super.initState();
    _fetchAlerts();
  }

  Future<void> _fetchAlerts() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });
    try {
      final inspections = await _inspectionService.fetchInspections();
      final alerts = inspections
          .where((alert) =>
              alert.severity != AlertSeverity.safe &&
              !_resolvedAlertIds.contains(alert.id))
          .toList();
      setState(() {
        _activeAlerts = alerts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _resolveAlert(String id) {
    setState(() {
      _resolvedAlertIds.add(id);
      _activeAlerts.removeWhere((alert) => alert.id == id);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(
          children: [
            Icon(Icons.check_circle_rounded, color: Colors.white),
            SizedBox(width: 8),
            Text('Alert acknowledged and resolved successfully.'),
          ],
        ),
        backgroundColor: Colors.green.shade700,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  void _handleAlertTap(AlertModel alert) async {
    // Show loading progress overlay
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      ),
    );

    try {
      final detail = await _inspectionService.fetchInspectionDetail(alert.id);
      if (mounted) {
        Navigator.pop(context); // Dismiss loading overlay
        _showConfirmationDialog(detail);
      }
    } catch (e) {
      if (mounted) {
        Navigator.pop(context); // Dismiss loading overlay
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load alert details: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  Color _severityColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.safe:
        return AppColors.safe;
      case AlertSeverity.low:
        return const Color(0xffB7E4C7);
      case AlertSeverity.medium:
        return AppColors.medium;
      case AlertSeverity.highRisk:
        return AppColors.highRisk;
    }
  }

  void _showConfirmationDialog(InspectionModel inspection) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          elevation: 12,
          backgroundColor: Colors.white,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Dialog Header
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 20, 20, 10),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                inspection.cameraId,
                                style: const TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.w900,
                                  color: AppColors.textDark,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${inspection.date} at ${inspection.time}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: AppColors.textGrey,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: _severityColor(inspection.severity),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            inspection.statusLabel,
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                              color: Colors.black87,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Image Preview
                  if (inspection.imageUrl.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.network(
                          inspection.imageUrl,
                          height: 180,
                          width: double.infinity,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Container(
                            height: 180,
                            color: Colors.grey.shade100,
                            child: const Icon(Icons.image_not_supported_outlined, size: 40, color: Colors.grey),
                          ),
                        ),
                      ),
                    ),

                  // Detections List
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 16, 20, 10),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Detected Items & Hazards',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textDark,
                          ),
                        ),
                        const SizedBox(height: 8),
                        if (inspection.detections.isEmpty)
                          const Text(
                            'No specific hazards cataloged.',
                            style: TextStyle(fontSize: 13, color: AppColors.textGrey),
                          )
                        else
                          ...inspection.detections.map((det) => Container(
                            margin: const EdgeInsets.only(bottom: 6),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: AppColors.background,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        det.displayLabel,
                                        style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: AppColors.textDark,
                                        ),
                                      ),
                                      if (det.geminiSuggestion.trim().isNotEmpty) ...[
                                        const SizedBox(height: 4),
                                        Text(
                                          det.geminiSuggestion,
                                          style: TextStyle(
                                            fontSize: 11,
                                            color: Colors.red.shade700,
                                            height: 1.3,
                                          ),
                                        ),
                                      ]
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: AppColors.border),
                                  ),
                                  child: Text(
                                    det.confidencePercent,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.primary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          )),
                      ],
                    ),
                  ),

                  // Actions
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        ElevatedButton(
                          onPressed: () {
                            Navigator.pop(context);
                            _resolveAlert(inspection.id);
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green.shade600,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            elevation: 0,
                          ),
                          child: const Text(
                            'Acknowledge & Resolve',
                            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton(
                                onPressed: () => Navigator.pop(context),
                                style: OutlinedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  side: const BorderSide(color: AppColors.border),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                child: const Text(
                                  'Cancel',
                                  style: TextStyle(color: AppColors.textGrey, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: OutlinedButton(
                                onPressed: () {
                                  Navigator.pop(context);
                                  Navigator.pushNamed(
                                    context,
                                    '/inspection-detail',
                                    arguments: inspection.toAlertModel(),
                                  );
                                },
                                style: OutlinedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  side: const BorderSide(color: AppColors.primary),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                child: const Text(
                                  'View Report',
                                  style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (!AuthSession.isSignedIn) {
      WidgetsBinding.instance?.addPostFrameCallback((_) {
        Navigator.pushReplacementNamed(context, AppRoutes.welcome);
      });
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(currentIndex: 2),
      body: SafeArea(
        child: Column(
          children: [
            // Header Section
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Active Alerts',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w900,
                      color: AppColors.textDark,
                      letterSpacing: -0.5,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: AppColors.primary),
                    onPressed: _fetchAlerts,
                  ),
                ],
              ),
            ),

            // Main Content Area
            Expanded(
              child: RefreshIndicator(
                onRefresh: _fetchAlerts,
                color: AppColors.primary,
                child: _buildAlertsContent(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertsContent() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      );
    }

    if (_errorMessage.isNotEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.15),
          const Icon(Icons.cloud_off_rounded, size: 54, color: AppColors.textGrey),
          const SizedBox(height: 16),
          const Center(
            child: Text(
              'Connection failed',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textDark),
            ),
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Text(
              _errorMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppColors.textGrey, fontSize: 13),
            ),
          ),
          const SizedBox(height: 20),
          Center(
            child: ElevatedButton.icon(
              onPressed: _fetchAlerts,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Try Again'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      );
    }

    if (_activeAlerts.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.18),
          const Icon(Icons.verified_user_rounded, size: 54, color: Colors.green),
          const SizedBox(height: 16),
          const Center(
            child: Text(
              'No active alerts',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textDark),
            ),
          ),
          const SizedBox(height: 6),
          const Center(
            child: Text(
              'All runway zones are reporting safe status.',
              style: TextStyle(color: AppColors.textGrey, fontSize: 14),
            ),
          ),
        ],
      );
    }

    return ListView.separated(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 110),
      itemCount: _activeAlerts.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final alert = _activeAlerts[index];
        return StaggeredSlideUp(
          index: index,
          child: AlertCard(
            alert: alert,
            onTap: () => _handleAlertTap(alert),
          ),
        );
      },
    );
  }
}

class StaggeredSlideUp extends StatefulWidget {
  const StaggeredSlideUp({
    super.key,
    required this.index,
    required this.child,
  });

  final int index;
  final Widget child;

  @override
  State<StaggeredSlideUp> createState() => _StaggeredSlideUpState();
}

class _StaggeredSlideUpState extends State<StaggeredSlideUp>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacity;
  late Animation<double> _slide;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 550),
    );

    _opacity = CurvedAnimation(parent: _controller, curve: Curves.easeIn);
    _slide = Tween<double>(begin: 24.0, end: 0.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutBack),
    );

    final delay = (widget.index * 60).clamp(0, 600);
    Future.delayed(Duration(milliseconds: delay), () {
      if (mounted) {
        _controller.forward();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Opacity(
          opacity: _opacity.value,
          child: Transform.translate(
            offset: Offset(0, _slide.value),
            child: child,
          ),
        );
      },
      child: widget.child,
    );
  }
}
