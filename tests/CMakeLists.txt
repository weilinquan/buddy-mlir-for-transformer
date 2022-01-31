configure_lit_site_cfg(
  ${CMAKE_CURRENT_SOURCE_DIR}/lit.site.cfg.py.in
  ${CMAKE_CURRENT_BINARY_DIR}/lit.site.cfg.py
  MAIN_CONFIG
  ${CMAKE_CURRENT_SOURCE_DIR}/lit.cfg.py
)

set(BUDDY_TEST_DEPENDS
  FileCheck count not
  buddy-opt
  buddy-translate
  )

add_lit_testsuite(check-buddy "Running the buddy regression tests"
  ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS ${BUDDY_TEST_DEPENDS}
  )
set_target_properties(check-buddy PROPERTIES FOLDER "Tests")

add_lit_testsuites(BUDDY ${CMAKE_CURRENT_SOURCE_DIR} DEPENDS ${BUDDY_TEST_DEPENDS})