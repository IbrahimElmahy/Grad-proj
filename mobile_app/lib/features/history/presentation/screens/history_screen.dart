import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../alerts/data/models/alert_model.dart';
import '../../../alerts/presentation/widgets/alert_card.dart';
import '../../../inspections/data/inspection_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final InspectionService _inspectionService = const InspectionService();
  bool _isLoading = true;
  String _errorMessage = '';
  List<AlertModel> _allAlerts = [];
  List<AlertModel> _filteredAlerts = [];
  String _searchQuery = '';
  String _selectedSeverity = 'All'; // 'All', 'Critical', 'Warning', 'Safe'

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });
    try {
      final data = await _inspectionService.fetchInspections();
      setState(() {
        _allAlerts = data;
        _isLoading = false;
        _applyFilters();
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _applyFilters() {
    setState(() {
      _filteredAlerts = _allAlerts.where((alert) {
        // Search filter
        final query = _searchQuery.toLowerCase();
        final matchesQuery = alert.runwayTitle.toLowerCase().contains(query) ||
            alert.statusText.toLowerCase().contains(query);

        // Severity filter
        bool matchesSeverity = true;
        if (_selectedSeverity == 'Critical') {
          matchesSeverity = alert.severity == AlertSeverity.highRisk;
        } else if (_selectedSeverity == 'Warning') {
          matchesSeverity = alert.severity == AlertSeverity.medium ||
              alert.severity == AlertSeverity.low;
        } else if (_selectedSeverity == 'Safe') {
          matchesSeverity = alert.severity == AlertSeverity.safe;
        }

        return matchesQuery && matchesSeverity;
      }).toList();
    });
  }

  Color _getChipColor(String type, bool isSelected) {
    if (!isSelected) return Colors.white;
    switch (type) {
      case 'Critical':
        return Colors.red.shade600;
      case 'Warning':
        return Colors.amber.shade600;
      case 'Safe':
        return Colors.green.shade600;
      default:
        return AppColors.primary;
    }
  }

  Color _getChipTextColor(String type, bool isSelected) {
    if (!isSelected) return AppColors.textGrey;
    return Colors.white;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(currentIndex: 1),
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
                    'Inspection History',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w900,
                      color: AppColors.textDark,
                      letterSpacing: -0.5,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: AppColors.primary),
                    onPressed: _fetchData,
                  ),
                ],
              ),
            ),

            // Search Bar Section
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: TextField(
                  onChanged: (val) {
                    _searchQuery = val;
                    _applyFilters();
                  },
                  decoration: InputDecoration(
                    hintText: 'Search runways or status...',
                    hintStyle: const TextStyle(color: AppColors.textGrey, fontSize: 15),
                    prefixIcon: const Icon(Icons.search_rounded, color: AppColors.primary),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? GestureDetector(
                            onTap: () {
                              setState(() {
                                _searchQuery = '';
                              });
                              _applyFilters();
                            },
                            child: const Icon(Icons.clear_rounded, color: AppColors.textGrey),
                          )
                        : null,
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  ),
                ),
              ),
            ),

            // Severity Filter Chips Section
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                children: ['All', 'Critical', 'Warning', 'Safe'].map((type) {
                  final isSelected = _selectedSeverity == type;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: InkWell(
                      onTap: () {
                        setState(() {
                          _selectedSeverity = type;
                        });
                        _applyFilters();
                      },
                      borderRadius: BorderRadius.circular(30),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 9),
                        decoration: BoxDecoration(
                          color: _getChipColor(type, isSelected),
                          borderRadius: BorderRadius.circular(30),
                          border: Border.all(
                            color: isSelected
                                ? _getChipColor(type, isSelected)
                                : AppColors.border,
                            width: 1.2,
                          ),
                          boxShadow: isSelected
                              ? [
                                  BoxShadow(
                                    color: _getChipColor(type, isSelected).withOpacity(0.24),
                                    blurRadius: 8,
                                    offset: const Offset(0, 3),
                                  ),
                                ]
                              : null,
                        ),
                        child: Text(
                          type,
                          style: TextStyle(
                            color: _getChipTextColor(type, isSelected),
                            fontWeight: FontWeight.w700,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),

            // Main List Section
            Expanded(
              child: RefreshIndicator(
                onRefresh: _fetchData,
                color: AppColors.primary,
                child: _buildListContent(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildListContent() {
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
              'Failed to load history',
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
              onPressed: _fetchData,
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

    if (_filteredAlerts.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.18),
          const Icon(Icons.inventory_2_outlined, size: 54, color: AppColors.textGrey),
          const SizedBox(height: 16),
          const Center(
            child: Text(
              'No inspections found',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppColors.textDark),
            ),
          ),
          const SizedBox(height: 6),
          const Center(
            child: Text(
              'Try altering your search or severity filters.',
              style: TextStyle(color: AppColors.textGrey, fontSize: 14),
            ),
          ),
        ],
      );
    }

    return ListView.separated(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 110),
      itemCount: _filteredAlerts.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final alert = _filteredAlerts[index];
        return StaggeredSlideUp(
          index: index,
          child: AlertCard(
            alert: alert,
            onTap: () {
              Navigator.pushNamed(
                context,
                '/inspection-detail',
                arguments: alert,
              );
            },
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
