from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('master/user/', views.user_index, name='user-index'),
    path('master/user/add/', views.user_add, name='user-add'),
    path('master/user/view/<str:_id>/', views.user_view, name='user-view'),
    path('master/user/update/<str:_id>/',
         views.user_update, name='user-update'),
    path('master/user/delete/<str:_id>/',
         views.user_delete, name='user-delete'),
    path('master/user/remove-signature/<str:_id>/',
         views.remove_signature, name='remove-signature'),
    path('master/user/change-password/',
         views.change_password, name='change-password'),
    path('master/user/set-password/<str:_id>/',
         views.set_password, name='set-password'),
    path('master/user-area/view/<str:_id>/',
         views.user_area_view, name='user-area-view'),
    path('master/distributor/', views.distributor_index, name='distributor-index'),
    path('master/distributor/add/', views.distributor_add, name='distributor-add'),
    path('master/distributor/view/<str:_id>/',
         views.distributor_view, name='distributor-view'),
    path('master/distributor/update/<str:_id>/',
         views.distributor_update, name='distributor-update'),
    path('master/distributor/delete/<str:_id>/',
         views.distributor_delete, name='distributor-delete'),
    path('master/area-sales/', views.area_sales_index, name='area-sales-index'),
    path('master/area-sales/add/', views.area_sales_add, name='area-sales-add'),
    path('master/area-sales/view/<str:_id>/',
         views.area_sales_view, name='area-sales-view'),
    path('master/area-sales/update/<str:_id>/',
         views.area_sales_update, name='area-sales-update'),
    path('master/area-sales/delete/<str:_id>/',
         views.area_sales_delete, name='area-sales-delete'),
    path('master/area-sales-detail/delete/<str:_id>/<str:_distributor>/',
         views.area_sales_detail_delete, name='area-sales-detail-delete'),
    path('master/position/', views.position_index, name='position-index'),
    path('master/position/add/', views.position_add, name='position-add'),
    path('master/position/view/<str:_id>/',
         views.position_view, name='position-view'),
    path('master/position/update/<str:_id>/',
         views.position_update, name='position-update'),
    path('master/position/delete/<str:_id>/',
         views.position_delete, name='position-delete'),
    path('master/menu/', views.menu_index, name='menu-index'),
    path('master/menu/add/', views.menu_add, name='menu-add'),
    path('master/menu/view/<str:_id>/', views.menu_view, name='menu-view'),
    path('master/menu/update/<str:_id>/',
         views.menu_update, name='menu-update'),
    path('master/menu/delete/<str:_id>/',
         views.menu_delete, name='menu-delete'),
    path('master/auth/update/<str:_id>/<str:_menu>/',
         views.auth_update, name='auth-update'),
    path('master/auth/delete/<str:_id>/<str:_menu>/',
         views.auth_delete, name='auth-delete'),
    path('master/area-user/delete/<str:_id>/<str:_area>/',
         views.area_user_delete, name='area-user-delete'),
    path('master/channel/', views.channel_index, name='channel-index'),
    path('master/channel/add/', views.channel_add, name='channel-add'),
    path('master/channel/view/<str:_id>/',
         views.channel_view, name='channel-view'),
    path('master/channel/update/<str:_id>/',
         views.channel_update, name='channel-update'),
    path('master/channel/delete/<str:_id>/',
         views.channel_delete, name='channel-delete'),
    path('master/area-channel/', views.area_channel_index,
         name='area-channel-index'),
    path('master/area-channel/add/',
         views.area_channel_add, name='area-channel-add'),
    path('master/area-channel/view/<str:_id>/',
         views.area_channel_view, name='area-channel-view'),
    path('master/area-channel/delete/<str:_id>/',
         views.area_channel_delete, name='area-channel-delete'),
    path('master/area-channel-detail/update/<str:_id>/<str:_channel>/',
         views.area_channel_detail_update, name='area-channel-detail-update'),
    path('master/closing-period/', views.closing_index, name='closing-index'),
    path('master/closing-period/add/', views.closing_add, name='closing-add'),
    path('master/closing-period/view/<str:_id>/',
         views.closing_view, name='closing-view'),
    path('master/closing-period/update/<str:_id>/', views.closing_update,
         name='closing-update'),
    path('master/closing-period/delete/<str:_id>/', views.closing_delete,
         name='closing-delete'),
    path('master/division/', views.division_index, name='division-index'),
    path('master/division/add/', views.division_add, name='division-add'),
    path('master/division/view/<str:_id>/',
         views.division_view, name='division-view'),
    path('master/division/update/<str:_id>/',
         views.division_update, name='division-update'),
    path('master/division/delete/<str:_id>/',
         views.division_delete, name='division-delete'),
    path('approval/budget/', views.budget_approval_index,
         name='budget-approval-index'),
    path('approval/budget/view/<str:_id>',
         views.budget_approval_view, name='budget-approval-view'),
    path('budget/<str:_tab>/', views.budget_index, name='budget-index'),
    path('budget/view/<str:_tab>/<path:_id>/<str:_msg>/',
         views.budget_view, name='budget-view'),
    path('budget/update/<str:_tab>/<path:_id>/',
         views.budget_update, name='budget-update'),
    path('budget/delete/<str:_tab>/<path:_id>/',
         views.budget_delete, name='budget-delete'),
    path('budget/submit/<path:_id>/', views.budget_submit, name='budget-submit'),
    path('budget_detail/update/<str:_tab>/<path:_id>/',
         views.budget_detail_update, name='budget-detail-update'),
    path('budget_upload/', views.budget_upload, name='budget-upload'),
    path('budget_upload/export-log/',
         views.export_uploadlog, name='export-uploadlog'),
    path('budget_upload/export-template/',
         views.export_budget_to_excel, name='export-budget-to-excel'),
    path('budget/add/<str:_area>/', views.budget_add, name='budget-add'),
    path('budget_transfer/<str:_tab>/', views.budget_transfer_index,
         name='budget-transfer-index'),
    path('budget_transfer/add/<str:_area>/<str:_distributor>/<path:_channel>/<str:_message>/',
         views.budget_transfer_add, name='budget-transfer-add'),
    path('budget_transfer/view/<str:_tab>/<path:_id>/',
         views.budget_transfer_view, name='budget-transfer-view'),
    path('budget_transfer/update/<path:_id>/<str:_area>/<str:_distributor>/<path:_channel>/<str:_message>/', views.budget_transfer_update,
         name='budget-transfer-update'),
    path('budget_transfer/delete/<path:_id>/',
         views.budget_transfer_delete, name='budget-transfer-delete'),
    path('budget_transfer/submit/<path:_id>/', views.budget_transfer_submit,
         name='budget-transfer-submit'),
    path('budget_transfer_release/', views.budget_transfer_release_index,
         name='budget-transfer-release-index'),
    path('budget_transfer_release/view/<path:_id>/<int:_is_revise>/',
         views.budget_transfer_release_view, name='budget-transfer-release-view'),
    path('budget_transfer_release/approve/<path:_id>/', views.budget_transfer_release_approve,
         name='budget-transfer-release-approve'),
    path('budget_transfer_release/return/<path:_id>/',
         views.budget_transfer_release_return, name='budget-transfer-release-return'),
    path('budget_release/', views.budget_release_index,
         name='budget-release-index'),
    path('budget_release/view/<path:_id>/<str:_msg>/<int:_is_revise>/',
         views.budget_release_view, name='budget-release-view'),
    path('budget_release/update/<path:_id>/',
         views.budget_release_update, name='budget-release-update'),
    path('budget_release/return/<path:_id>/',
         views.budget_release_return, name='budget-release-return'),
    path('budget_detail_release/update/<path:_id>/',
         views.budget_detail_release_update, name='budget-detail-release-update'),
    path('budget_release/approve/<path:_id>/',
         views.budget_release_approve, name='budget-release-approve'),
    path('proposal_release/', views.proposal_release_index,
         name='proposal-release-index'),
    path('proposal_release/view/<path:_id>/<str:_sub_id>/<str:_act>/<str:_msg>/<int:_is_revise>/',
         views.proposal_release_view, name='proposal-release-view'),
    path('proposal_release_incremental/add/<path:_id>/',
         views.proposal_release_incremental_add, name='proposal-release-incremental-add'),
    path('proposal_release_incremental/update/<path:_id>/<str:_product>/',
         views.proposal_release_incremental_update, name='proposal-release-incremental-update'),
    path('proposal_release_incremental/delete/<path:_id>/<str:_product>/',
         views.proposal_release_incremental_delete, name='proposal-release-incremental-delete'),
    path('proposal_release_cost/add/<path:_id>/',
         views.proposal_release_cost_add, name='proposal-release-cost-add'),
    path('proposal_release_cost/delete/<path:_id>/<str:_activities>/',
         views.proposal_release_cost_delete, name='proposal-release-cost-delete'),
    path('proposal_release_cost/update/<path:_id>/<str:_activities>/',
         views.proposal_release_cost_update, name='proposal-release-cost-update'),
    path('proposal_release/approve/<path:_id>/',
         views.proposal_release_approve, name='proposal-release-approve'),
    path('proposal_release/update/<path:_id>/',
         views.proposal_release_update, name='proposal-release-update'),
    path('proposal_release/return/<path:_id>/',
         views.proposal_release_return, name='proposal-release-return'),
    path('proposal_release/reject/<path:_id>/',
         views.proposal_release_reject, name='proposal-release-reject'),
    path('proposal_print/<path:_id>/',
         views.proposal_print, name='proposal-print'),
    path('budget_archive/', views.budget_archive_index,
         name='budget-archive-index'),
    path('proposal_archive/<str:_tab>', views.proposal_archive_index,
         name='proposal-archive-index'),
    path('approval/budget/', views.budget_approval_index,
         name='budget-approval-index'),
    path('approval/budget/view/<str:_id>/',
         views.budget_approval_view, name='budget-approval-view'),
    path('approval/budget/update/<str:_id>/<str:_approver>/',
         views.budget_approval_update, name='budget-approval-update'),
    path('approval/budget/delete/<str:_id>/<str:_arg>/',
         views.budget_approval_delete, name='budget-approval-delete'),
    path('matrix/budget_transfer/', views.budget_transfer_matrix_index,
         name='budget-transfer-matrix-index'),
    path('matrix/budget_transfer/view/<str:_area>/',
         views.budget_transfer_matrix_view, name='budget-transfer-matrix-view'),
    path('matrix/budget_transfer/update/<str:_area>/<str:_id>/',
         views.budget_transfer_matrix_update, name='budget-transfer-matrix-update'),
    path('matrix/budget_transfer/delete/<str:_area>/<str:_id>/',
         views.budget_transfer_matrix_delete, name='budget-transfer-matrix-delete'),
    path('matrix/proposal/', views.proposal_matrix_index,
         name='proposal-matrix-index'),
    path('matrix/proposal/view/<str:_id>/<str:_channel>/',
         views.proposal_matrix_view, name='proposal-matrix-view'),
    path('matrix/proposal/update/<str:_id>/<str:_channel>/<str:_approver>/',
         views.proposal_matrix_update, name='proposal-matrix-update'),
    path('matrix/proposal/delete/<str:_id>/<str:_channel>/<str:_arg>/',
         views.proposal_matrix_delete, name='proposal-matrix-delete'),
    path('closing/', views.closing, name='closing'),
    path('proposal/<str:_tab>/', views.proposal_index, name='proposal-index'),
    path('proposal/add/<str:_area>/<path:_budget>/<str:_channel>/',
         views.proposal_add, name='proposal-add'),
    path('proposal/view/<str:_tab>/<path:_id>/<str:_sub_id>/<str:_act>/<str:_msg>/',
         views.proposal_view, name='proposal-view'),
    path('proposal/update/<str:_tab>/<path:_id>/',
         views.proposal_update, name='proposal-update'),
    path('proposal/delete/<str:_tab>/<path:_id>/',
         views.proposal_delete, name='proposal-delete'),
    path('proposal/submit/<path:_id>/',
         views.proposal_submit, name='proposal-submit'),
    path('proposal/add-attachment/<str:_tab>/<path:_id>/', views.proposal_attachment_add,
         name='proposal-attachment-add'),
    path('proposal/remove-attachment/<str:_tab>/<path:_id>/',
         views.remove_attachment, name='remove-attachment'),
    path('proposal_release/remove-release-attachment/<path:_id>/',
         views.remove_release_attachment, name='remove-release-attachment'),
    path('proposal_incremental/add/<str:_tab>/<path:_id>/', views.proposal_incremental_add,
         name='proposal-incremental-add'),
    path('proposal_incremental/update/<str:_tab>/<path:_id>/<str:_product>/', views.proposal_incremental_update,
         name='proposal-incremental-update'),
    path('proposal_incremental/delete/<str:_tab>/<path:_id>/<str:_product>/',
         views.proposal_incremental_delete, name='proposal-incremental-delete'),
    path('proposal_cost/add/<str:_tab>/<path:_id>/',
         views.proposal_cost_add, name='proposal-cost-add'),
    path('proposal_cost/delete/<str:_tab>/<path:_id>/<str:_activities>/', views.proposal_cost_delete,
         name='proposal-cost-delete'),
    path('proposal_cost/update/<str:_tab>/<path:_id>/<str:_activities>/', views.proposal_cost_update,
         name='proposal-cost-update'),
    path('closing/proposal/', views.proposal_closing_index,
         name='proposal-closing-index'),
    path('closing/proposal/bulk/', views.proposal_bulk_close,
         name='proposal-bulk-close'),
    path('closing/proposal/single/<path:_id>/', views.proposal_single_close,
         name='proposal-single-close'),
    path('program/<str:_tab>/', views.program_index, name='program-index'),
    path('program/add/<str:_area>/<str:_distributor>/<path:_proposal>/',
         views.program_add, name='program-add'),
    path('program/view/<str:_tab>/<path:_id>/',
         views.program_view, name='program-view'),
    path('program/update/<str:_tab>/<path:_id>/',
         views.program_update, name='program-update'),
    path('program/delete/<str:_tab>/<path:_id>/',
         views.program_delete, name='program-delete'),
    path('program/submit/<path:_id>/',
         views.program_submit, name='program-submit'),
    path('program_release/', views.program_release_index,
         name='program-release-index'),
    path('program_release/view/<path:_id>/<int:_is_revise>/',
         views.program_release_view, name='program-release-view'),
    path('program_release/update/<path:_id>/',
         views.program_release_update, name='program-release-update'),
    path('program_release/approve/<path:_id>/',
         views.program_release_approve, name='program-release-approve'),
    path('program_release/return/<path:_id>/',
         views.program_release_return, name='program-release-return'),
    path('program_release/reject/<path:_id>/',
         views.program_release_reject, name='program-release-reject'),
    path('program_archive/', views.program_archive_index,
         name='program-archive-index'),
    path('program_print/<path:_id>/',
         views.program_print, name='program-print'),
    path('matrix/program/', views.program_matrix_index,
         name='program-matrix-index'),
    path('matrix/program/view/<str:_id>/<str:_channel>/',
         views.program_matrix_view, name='program-matrix-view'),
    path('matrix/program/update/<str:_id>/<str:_channel>/<str:_approver>/',
         views.program_matrix_update, name='program-matrix-update'),
    path('matrix/program/delete/<str:_id>/<str:_channel>/<str:_arg>/',
         views.program_matrix_delete, name='program-matrix-delete'),
    path('claim/<str:_tab>/', views.claim_index, name='claim-index'),
    path('claim/add/<str:_area>/<str:_distributor>/<path:_program>/',
         views.claim_add, name='claim-add'),
    path('claim/view/<str:_tab>/<path:_id>/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.claim_view, name='claim-view'),
    path('claim/update/<str:_tab>/<path:_id>/',
         views.claim_update, name='claim-update'),
    path('claim/delete/<str:_tab>/<path:_id>/',
         views.claim_delete, name='claim-delete'),
    path('claim/submit/<path:_id>/', views.claim_submit, name='claim-submit'),
    path('claim_release/', views.claim_release_index,
         name='claim-release-index'),
    path('claim_release/view/<path:_id>/<int:_is_revise>/',
         views.claim_release_view, name='claim-release-view'),
    path('claim_release/update/<path:_id>/',
         views.claim_release_update, name='claim-release-update'),
    path('claim_release/approve/<path:_id>/',
         views.claim_release_approve, name='claim-release-approve'),
    path('claim_release/bulk-approve/', views.claim_release_bulk_approve,
         name='claim-release-bulk-approve'),
    path('claim_release/return/<path:_id>/',
         views.claim_release_return, name='claim-release-return'),
    path('claim_release/reject/<path:_id>/',
         views.claim_release_reject, name='claim-release-reject'),
    path('claim_archive/', views.claim_archive_index, name='claim-archive-index'),
    path('matrix/claim/', views.claim_matrix_index,
         name='claim-matrix-index'),
    path('matrix/claim/view/<str:_id>/<str:_channel>/',
         views.claim_matrix_view, name='claim-matrix-view'),
    path('matrix/claim/update/<str:_id>/<str:_channel>/<str:_approver>/',
         views.claim_matrix_update, name='claim-matrix-update'),
    path('matrix/claim/delete/<str:_id>/<str:_channel>/<str:_arg>/',
         views.claim_matrix_delete, name='claim-matrix-delete'),
    path('claim_print/<path:_id>/',
         views.claim_print, name='claim-print'),
    path('cl/<str:_tab>/', views.cl_index, name='cl-index'),
    path('cl/add/<str:_area>/<str:_distributor>/', views.cl_add, name='cl-add'),
    path('cl/view/<str:_tab>/<path:_id>/',
         views.cl_view, name='cl-view'),
    path('cl/delete/<str:_tab>/<path:_id>/',
         views.cl_delete, name='cl-delete'),
    path('cl/submit/<path:_id>/', views.cl_submit, name='cl-submit'),
    path('cl_detail/delete/<str:_tab>/<int:_id>/',
         views.cldetail_delete, name='cldetail-delete'),
    path('cl_release/', views.cl_release_index,
         name='cl-release-index'),
    path('cl_release/view/<path:_id>/<int:_is_revise>/',
         views.cl_release_view, name='cl-release-view'),
    path('cl_detail_release/delete/<int:_id>/',
         views.cldetail_release_delete, name='cldetail-release-delete'),
    path('cl_release/update/<path:_id>/',
         views.cl_release_update, name='cl-release-update'),
    path('cl_release/approve/<path:_id>/',
         views.cl_release_approve, name='cl-release-approve'),
    path('cl_release/return/<path:_id>/',
         views.cl_release_return, name='cl-release-return'),
    path('cl_release/reject/<path:_id>/',
         views.cl_release_reject, name='cl-release-reject'),
    path('cl_archive/', views.cl_archive_index, name='cl-archive-index'),
    path('matrix/cl/', views.cl_matrix_index, name='cl-matrix-index'),
    path('matrix/cl/view/<str:_id>/', views.cl_matrix_view, name='cl-matrix-view'),
    path('matrix/cl/update/<str:_id>/<str:_approver>/',
         views.cl_matrix_update, name='cl-matrix-update'),
    path('matrix/cl/delete/<str:_id>/<str:_arg>/',
         views.cl_matrix_delete, name='cl-matrix-delete'),
    path('cl_print/<path:_id>/', views.cl_print, name='cl-print'),
    path('master/region/', views.region_index, name='region-index'),
    path('master/region/add/', views.region_add, name='region-add'),
    path('master/region/view/<str:_id>/',
         views.region_view, name='region-view'),
    path('master/region/update/<str:_id>/',
         views.region_update, name='region-update'),
    path('master/region/delete/<str:_id>/',
         views.region_delete, name='region-delete'),
    path('master/region-detail/delete/<str:_id>/<str:_area>/',
         views.region_detail_delete, name='region-detail-delete'),
    path('report/transfer/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.report_transfer, name='report-transfer'),
    path('report/cl/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.report_cl, name='report-cl'),
    path('report/claim/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.report_claim, name='report-claim'),
    path('report/proposal_claim/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.report_proposal_claim, name='report-proposal-claim'),
    path('report/proposal/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.report_proposal, name='report-proposal'),
    path('report/budget/monthly/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.report_monthly_budget, name='report-monthly-budget'),
    path('report/budget_summary/<str:_from_yr>/<str:_from_mo>/<str:_to_yr>/<str:_to_mo>/<str:_distributor>/',
         views.report_budget_summary, name='report-budget-summary'),
]
