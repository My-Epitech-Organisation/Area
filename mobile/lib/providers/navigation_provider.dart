import 'package:flutter/material.dart';

class NavigationProvider extends ChangeNotifier {
  int _currentPage = 0;
  final PageController _pageController = PageController();

  int get currentPage => _currentPage;
  PageController get pageController => _pageController;

  void navigateToPage(int pageIndex) {
    if (pageIndex != _currentPage) {
      _pageController.animateToPage(
        pageIndex,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeInOutCubic,
      );
    }
  }

  void updateCurrentPage(int pageIndex) {
    _currentPage = pageIndex;
    notifyListeners();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }
}
