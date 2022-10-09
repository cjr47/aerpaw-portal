"""
Define the following for each transition between states
- PREFLIGHT CHECK: Preflight validation for requested state change / logic / data collection
- ACTION ITEMS: Transition action items (e.g. start/stop Session)
- UPDATE STATE: Update experiment state
- PORTAL CF: portal control framework decision points
"""

import os
import threading
import time

from rest_framework.exceptions import NotFound, ValidationError

from portal.apps.credentials.models import PublicCredentials
from portal.apps.experiments.api.experiment_sessions import cancel_experiment_session, create_experiment_session, \
    start_experiment_session, stop_experiment_session
from portal.apps.experiments.models import AerpawExperiment, ExperimentSession
from portal.server.ops_ssh_utils import AerpawSsh
from portal.server.settings import MOCK_OPS

aerpaw_ops_host = os.getenv('AERPAW_OPS_HOST')
aerpaw_ops_port = os.getenv('AERPAW_OPS_PORT')
aerpaw_ops_user = os.getenv('AERPAW_OPS_USER')
aerpaw_ops_key_file = os.getenv('AERPAW_OPS_KEY_FILE')
_TMP_FILE_PATH = '/tmp/aerpaw_files'


def active_development_to_save_development(request, experiment: AerpawExperiment):
    """
    ACTIVE_DEVELOPMENT --> SAVE_DEVELOPMENT
    - save development session

    @param: exit_development

    Session: update DEVELOPMENT --> no change

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))

    # UPDATE STATE: save_development
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVE_DEVELOPMENT
    experiment.save()
    # check exit_development flag
    try:
        exit_development = request.data.get('exit_development', False)
    except Exception as exc:
        print(exc)
        exit_development = False

    # PORTAL CF: save_development
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT>
    if MOCK_OPS:
        # MOCK OPS: always pass
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)
        # MOCK OPS: always fail
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_failure.py {0}".format(
        #     experiment.id)
    else:
        # PRODUCTION:
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/apcf_deploy_ve_exp.py {0}".format(experiment.id)
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)

    ssh_thread = threading.Thread(target=save_development, args=(request, experiment, command, exit_development))
    ssh_thread.start()


def active_sandbox_to_save_sandbox(request, experiment: AerpawExperiment):
    """
    ACTIVE_SANDBOX --> SAVE_SANDBOX
    - save sandbox session

    @param: exit_sandbox

    Session: update SANDBOX --> no change

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))

    # UPDATE STATE: save_sandbox
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVE_SANDBOX
    experiment.save()

    # check exit_sandbox flag
    try:
        exit_sandbox = request.data.get('exit_sandbox', False)
    except Exception as exc:
        print(exc)
        exit_sandbox = False

    # PORTAL CF: save_sandbox
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT>
    if MOCK_OPS:
        # MOCK OPS: always pass
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)
        # MOCK OPS: always fail
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_failure.py {0}".format(
        #     experiment.id)
    else:
        # PRODUCTION:
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/apcf_deploy_ve_exp.py {0}".format(experiment.id)
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)

    ssh_thread = threading.Thread(target=save_sandbox, args=(request, experiment, command, exit_sandbox))
    ssh_thread.start()


def save_development_to_saved(request, experiment: AerpawExperiment):
    """
    SAVE_DEVELOPMENT --> SAVED
    - save development session
    - Flags 000 (e.g. experimenter logged out of all VMs for one hour)

    Session: update DEVELOPMENT --> end_date_time, ended_by, is_active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()

    # PORTAL CF:


def save_development_to_wait_development_deploy(request, experiment: AerpawExperiment):
    """
    SAVE_DEVELOPMENT --> WAIT_DEVELOPMENT_DEPLOY
    - resume development session

    Session: resume DEVELOPMENT --> no change

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))

    # UPDATE STATE: wait_development_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY
    experiment.save()

    # PORTAL CF: wait_development_deploy
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT>
    if MOCK_OPS:
        # MOCK OPS: always pass
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)
        # MOCK OPS: always fail
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_failure.py {0}".format(
        #     experiment.id)
    else:
        # PRODUCTION:
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/apcf_deploy_ve_exp.py {0}".format(experiment.id)
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)

    ssh_thread = threading.Thread(target=wait_development_deploy, args=(request, experiment, command))
    ssh_thread.start()


def save_sandbox_to_saved(request, experiment: AerpawExperiment):
    """
    SAVE_SANDBOX --> SAVED
    - save sandbox session
    - Flags 000 (e.g. end of scheduled sandbox session)

    Session: update SANDBOX --> end_date_time, ended_by, is_active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()

    # PORTAL CF:


def save_sandbox_to_wait_sandbox_deploy(request, experiment: AerpawExperiment):
    """
    SAVE_SANDBOX --> WAIT_SANDBOX_DEPLOY
    - resume sandbox session

    Session: resume SANDBOX --> created, created_by

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY
    experiment.experiment_flags = '000'
    experiment.save()

    # PORTAL CF: wait_sandbox_deploy
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT>
    if MOCK_OPS:
        # MOCK OPS: always pass
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)
        # MOCK OPS: always fail
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_failure.py {0}".format(
        #     experiment.id)
    else:
        # PRODUCTION:
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/apcf_deploy_ve_exp.py {0}".format(experiment.id)
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)

    ssh_thread = threading.Thread(target=wait_sandbox_deploy, args=(request, experiment, command))
    ssh_thread.start()


def active_emulation_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_EMULATION --> SAVED
    - emulation complete
    - Flags 100 or 101

    @param: emulation_passed

    Session: update EMULATION --> end_date_time, ended_by, is_active=False

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    try:
        emulation_passed = request.data.get('emulation_passed', False)
    except Exception as exc:
        print(exc)
        emulation_passed = False
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    if emulation_passed:
        experiment.experiment_flags = '101'
    else:
        experiment.experiment_flags = '100'
    experiment.save()


def active_testbed_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_TESTBED --> SAVED
    - execution complete
    - Flags 010

    Session: update TESTBED --> end_date_time, ended_by, is_active=False

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '010'
    experiment.save()


def saved_to_wait_development_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_DEVELOPMENT_DEPLOY
    - start development session

    Session: create DEVELOPMENT --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:
    # experiment has one or more resources
    if not experiment.resources.exists():
        raise ValidationError(
            detail="ValidationError: one or more resources required for /experiments/{0}/state".format(experiment.id))
    # user has one or more credentials
    if not PublicCredentials.objects.filter(
            owner=request.user,
            is_deleted=False
    ).exists():
        raise ValidationError(
            detail="ValidationError: one or more user credentials required for /experiments/{0}/state".format(
                experiment.id))

    # ACTION ITEMS:
    # lock experiment resources from being further modified
    experiment.resources_locked = True
    experiment.save()
    # create new DEVELOPMENT session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        experiment=experiment,
        user=request.user
    )

    # UPDATE STATE: wait_development_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY
    experiment.save()

    # PORTAL CF:
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # aerpaw ops: apcf_deploy_ve_exp.py
    if MOCK_OPS:
        # MOCK OPS: always pass
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)
        # MOCK OPS: always fail
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_failure.py {0}".format(
        #     experiment.id)
    else:
        # PRODUCTION:
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/apcf_deploy_ve_exp.py {0}".format(experiment.id)

    ssh_thread = threading.Thread(target=wait_development_deploy, args=(request, experiment, command))
    ssh_thread.start()


def saved_to_wait_sandbox_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_SANDBOX_DEPLOY
    - schedule sandbox session

    Session: create SANDBOX --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # create new SANDBOX session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.SANDBOX,
        experiment=experiment,
        user=request.user
    )

    # UPDATE STATE: wait_sandbox_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY
    experiment.save()

    # PORTAL CF: wait_sandbox_deploy
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT>
    if MOCK_OPS:
        # MOCK OPS: always pass
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)
        # MOCK OPS: always fail
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_failure.py {0}".format(
        #     experiment.id)
    else:
        # PRODUCTION:
        # command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/apcf_deploy_ve_exp.py {0}".format(experiment.id)
        command = "/home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
            experiment.id)

    ssh_thread = threading.Thread(target=wait_sandbox_deploy, args=(request, experiment, command))
    ssh_thread.start()


def saved_to_wait_emulation_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_EMULATION_SCHEDULE
    - reqeust emulation session

    Session: create EMULATION --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # create new EMULATION session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.EMULATION,
        experiment=experiment,
        user=request.user
    )

    # UPDATE STATE: wait_emulation_schedule
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE
    experiment.save()


def saved_to_wait_testbed_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_TESTBED_SCHEDULE
    - request testbed session (allowed if (E&&P)|T

    Session: create TESTBED --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # create new TESTBED session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.TESTBED,
        experiment=experiment,
        user=request.user
    )

    # UPDATE STATE: wait_testbed_schedule
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE
    experiment.save()


def wait_development_deploy_to_active_development(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> ACTIVE_DEVELOPMENT
    - deployment on development VMs complete

    Session: update DEVELOPMENT --> start_date_time, started_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    # start session if not already running
    if not session.start_date_time:
        start_experiment_session(session=session, user=request.user)

    # UPDATE STATE: active_development
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT
    experiment.experiment_flags = '000'
    experiment.save()


def wait_development_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Session: update DEVELOPMENT --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    # stop session if it was previously running
    if session.start_date_time:
        stop_experiment_session(session=session, user=request.user)
    # otherwise cancel the session if it has not yet started
    else:
        cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_emulation_deploy_to_active_emulation(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_DEPLOY --> ACTIVE_EMULATION
    - scheduled deployment of emulation complete

    Session: update EMULATION --> start_date_time, started_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    start_experiment_session(session=session, user=request.user)

    # UPDATE STATE: active_emulation
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_EMULATION
    experiment.save()


def wait_emulation_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Session: update EMULATION --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_emulation_schedule_to_wait_emulation_deploy(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> WAIT_EMULATION_DEPLOY
    - schedule

    Session: update EMULATION --> active=True

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # no change to session

    # UPDATE STATE: wait_emulation_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_DEPLOY
    experiment.save()


def wait_emulation_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> SAVED
    - cancel pending emulation session

    Session: update EMULATION --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_sandbox_deploy_to_active_sandbox(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> ACTIVE_SANDBOX
    - scheduled deployment on sandbox complete

    Session: update SANDBOX --> start_date_time, started_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    # start session if not already running
    if not session.start_date_time:
        start_experiment_session(session=session, user=request.user)

    # UPDATE STATE: active_sandbox
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_SANDBOX
    experiment.experiment_flags = '000'
    experiment.save()


def wait_sandbox_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> SAVED
    - cancel pending sandbox session

    Session: update SANDBOX --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    # stop session if it was previously running
    if session.start_date_time:
        stop_experiment_session(session=session, user=request.user)
    # otherwise cancel the session if it has not yet started
    else:
        cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_testbed_deploy_to_active_testbed(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> ACTIVE_TESTBED
    - scheduled deployment of testbed complete

    Session: update TESTBED --> start_date_time, started_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    start_experiment_session(session=session, user=request.user)

    # UPDATE STATE: active_testbed
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_TESTBED
    experiment.save()


def wait_testbed_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> SAVED
    - cancel

    Session: update TESTBED --> active=False

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_testbed_schedule_to_wait_testbed_deploy(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> WAIT_TESTBED_DEPLOY
    - schedule

    Session: update TESTBED --> active=True

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # no change to session

    # UPDATE STATE: wait_testbed_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY
    experiment.save()


def wait_testbed_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> SAVED
    - cancel pending testbed session

    Session: update TESTBED --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def same_to_same(request, experiment: AerpawExperiment):
    """
    Placeholder for same state update options

    Permissions:
    - experimenter OR
    - operator
    """
    # TODO: placeholder for same state update options
    # PREFLIGHT CHECK:
    # ACTION ITEMS:
    # UPDATE STATE:
    print(experiment.experiment_state)


def save_development(request, experiment: AerpawExperiment, command: str, exit_development: bool):
    # TODO: placeholder for save_development
    # ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
    # response, exit_code = ssh_call.send_command(command, verbose=True)
    response = '{"msg": "SaveDevelopment: saving development data", "urn": "/test"}'
    exit_code = 0
    if MOCK_OPS:
        # add sleep when using mock to simulate remote procession delay
        time.sleep(5)
        print('response: ' + response)
        print('exit code: ' + str(exit_code))

    # next state transition
    if exit_development:
        # save_development --> saved
        save_development_to_saved(request=request, experiment=experiment)
    else:
        # save_development --> wait_development_deploy
        save_development_to_wait_development_deploy(request=request, experiment=experiment)


def save_sandbox(request, experiment: AerpawExperiment, command: str, exit_sandbox: bool):
    # TODO: placeholder for save_sandbox
    # ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
    # response, exit_code = ssh_call.send_command(command, verbose=True)
    response = '{"msg": "SaveSandbox: saving sandbox data", "urn": "/test"}'
    exit_code = 0
    if MOCK_OPS:
        # add sleep when using mock to simulate remote procession delay
        time.sleep(5)
        print('response: ' + response)
        print('exit code: ' + str(exit_code))

    # next state transition
    if exit_sandbox:
        # save_sandbox --> saved
        save_sandbox_to_saved(request=request, experiment=experiment)
    else:
        # save_sandbox --> wait_sandbox_deploy
        save_sandbox_to_wait_sandbox_deploy(request=request, experiment=experiment)


def wait_development_deploy(request, experiment: AerpawExperiment, command: str) -> None:
    ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
    response, exit_code = ssh_call.send_command(command, verbose=True)
    if MOCK_OPS:
        # add sleep when using mock to simulate remote procession delay
        time.sleep(10)
        print('response: ' + response)
        print('exit code: ' + str(exit_code))

    # next state transition
    if exit_code == 0:
        # apcf_deploy_ve_exp - success
        # - wait_development_deploy --> active_development
        wait_development_deploy_to_active_development(request=request, experiment=experiment)
    else:
        # apcf_deploy_ve_exp - failure
        # - wait_development_deploy --> saved
        wait_development_deploy_to_saved(request=request, experiment=experiment)
        raise NotFound(
            detail="DeployError: unable to deploy active_development for /experiments/{0}/state".format(experiment.id))


def wait_sandbox_deploy(request, experiment: AerpawExperiment, command: str):
    # TODO: placeholder for wait_sandbox_deploy
    # ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
    # response, exit_code = ssh_call.send_command(command, verbose=True)
    response = '{"msg": "WaitSandboxDeploy: deploying sandbox", "urn": "/test"}'
    exit_code = 0
    if MOCK_OPS:
        # add sleep when using mock to simulate remote procession delay
        time.sleep(10)
        print('response: ' + response)
        print('exit code: ' + str(exit_code))

    # next state transition
    if exit_code == 0:
        # - wait_sandbox_deploy --> active_sandbox
        wait_sandbox_deploy_to_active_sandbox(request=request, experiment=experiment)
    else:
        # - wait_sandbox_deploy --> saved
        wait_sandbox_deploy_to_saved(request=request, experiment=experiment)
        raise NotFound(
            detail="DeployError: unable to deploy active_sandbox for /experiments/{0}/state".format(experiment.id))
