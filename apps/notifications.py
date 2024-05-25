from django.db import connection


def budget_notification(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_budget.budget_id, apps_distributor.distributor_name, apps_budget.budget_amount, apps_budget.budget_upping, apps_budget.budget_total, apps_budget.budget_status, apps_budgetrelease.sequence FROM apps_distributor INNER JOIN apps_budget ON apps_distributor.distributor_id = apps_budget.budget_distributor_id INNER JOIN apps_budgetrelease ON apps_budget.budget_id = apps_budgetrelease.budget_id INNER JOIN (SELECT budget_id, MIN(sequence) AS seq FROM apps_budgetrelease WHERE budget_approval_status = 'N' GROUP BY budget_id ORDER BY sequence ASC) AS q_group ON apps_budgetrelease.budget_id = q_group.budget_id AND apps_budgetrelease.sequence = q_group.seq WHERE (apps_budget.budget_status = 'IN APPROVAL') AND apps_budgetrelease.budget_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    return len(list(release)) if release else 0


def proposal_notification(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_proposal.proposal_id, apps_proposal.proposal_date, apps_proposal.channel, apps_division.division_name, apps_proposal.total_cost, apps_proposal.status, apps_proposal.reference, apps_proposalrelease.sequence FROM apps_division INNER JOIN apps_proposal ON apps_division.division_id = apps_proposal.division_id INNER JOIN apps_proposalrelease ON apps_proposal.proposal_id = apps_proposalrelease.proposal_id INNER JOIN (SELECT proposal_id, MIN(sequence) AS seq FROM apps_proposalrelease WHERE proposal_approval_status = 'N' GROUP BY proposal_id ORDER BY sequence ASC) AS q_group ON apps_proposalrelease.proposal_id = q_group.proposal_id AND apps_proposalrelease.sequence = q_group.seq WHERE (apps_proposal.status = 'PENDING' OR apps_proposal.status = 'IN APPROVAL') AND apps_proposalrelease.proposal_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    return len(list(release)) if release else 0


def program_notification(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_program.program_id, apps_program.program_date, apps_distributor.distributor_name, apps_proposal.channel, apps_program.status, apps_programrelease.sequence FROM apps_distributor INNER JOIN apps_budget ON apps_distributor.distributor_id = apps_budget.budget_distributor_id INNER JOIN apps_proposal ON apps_budget.budget_id = apps_proposal.budget_id INNER JOIN apps_program ON apps_proposal.proposal_id = apps_program.proposal_id INNER JOIN apps_programrelease ON apps_program.program_id = apps_programrelease.program_id INNER JOIN (SELECT program_id, MIN(sequence) AS seq FROM apps_programrelease WHERE program_approval_status = 'N' GROUP BY program_id ORDER BY sequence ASC) AS q_group ON apps_programrelease.program_id = q_group.program_id AND apps_programrelease.sequence = q_group.seq WHERE (apps_program.status = 'PENDING' OR apps_program.status = 'IN APPROVAL') AND apps_programrelease.program_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    return len(list(release)) if release else 0


def claim_notification(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_claim.claim_id, apps_claim.claim_date, apps_distributor.distributor_name, apps_proposal.channel, apps_claim.total_claim, apps_claim.status, apps_claimrelease.sequence FROM apps_distributor INNER JOIN apps_budget ON apps_distributor.distributor_id = apps_budget.budget_distributor_id INNER JOIN apps_proposal ON apps_budget.budget_id = apps_proposal.budget_id INNER JOIN apps_claim ON apps_proposal.proposal_id = apps_claim.proposal_id INNER JOIN apps_claimrelease ON apps_claim.claim_id = apps_claimrelease.claim_id INNER JOIN (SELECT claim_id, MIN(sequence) AS seq FROM apps_claimrelease WHERE claim_approval_status = 'N' AND approve = 1 GROUP BY claim_id ORDER BY sequence ASC) AS q_group ON apps_claimrelease.claim_id = q_group.claim_id AND apps_claimrelease.sequence = q_group.seq WHERE (apps_claim.status = 'PENDING' OR apps_claim.status = 'IN APPROVAL') AND apps_claimrelease.claim_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    return len(list(release)) if release else 0


def cl_notification(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_cl.cl_id, apps_cl.cl_date, apps_cl.area_id, apps_distributor.distributor_name, sum_total_claim, apps_cl.status, apps_clrelease.sequence FROM apps_distributor INNER JOIN apps_cl ON apps_distributor.distributor_id = apps_cl.distributor_id INNER JOIN apps_clrelease ON apps_cl.cl_id = apps_clrelease.cl_id_id INNER JOIN (SELECT cl_id_id, MIN(sequence) AS seq FROM apps_clrelease WHERE cl_approval_status = 'N' GROUP BY cl_id_id ORDER BY sequence ASC) AS q_group ON apps_clrelease.cl_id_id = q_group.cl_id_id AND apps_clrelease.sequence = q_group.seq LEFT JOIN (SELECT cl_id_id, sum(total_claim) AS sum_total_claim FROM apps_cldetail INNER JOIN apps_claim ON apps_cldetail.claim_id = apps_claim.claim_id WHERE apps_claim.status = 'OPEN' GROUP BY cl_id_id) AS q_cldetail ON apps_cl.cl_id = q_cldetail.cl_id_id WHERE (apps_cl.status = 'PENDING' OR apps_cl.status = 'IN APPROVAL') AND apps_clrelease.cl_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    return len(list(release)) if release else 0
