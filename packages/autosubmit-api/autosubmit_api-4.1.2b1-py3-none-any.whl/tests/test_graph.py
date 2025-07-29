from autosubmit_api.builders.configuration_facade_builder import (
    AutosubmitConfigurationFacadeBuilder,
    ConfigurationFacadeDirector,
)
from autosubmit_api.builders.joblist_loader_builder import (
    JobListLoaderBuilder,
    JobListLoaderDirector,
)
from autosubmit_api.database.db_jobdata import ExperimentGraphDrawing
from autosubmit_api.monitor.monitor import Monitor
from autosubmit_api.repositories.graph_layout import create_exp_graph_layout_repository


class TestPopulateDB:
    def test_monitor_dot(self, fixture_mock_basic_config):
        expid = "a003"
        job_list_loader = JobListLoaderDirector(
            JobListLoaderBuilder(expid)
        ).build_loaded_joblist_loader()

        monitor = Monitor()
        graph = monitor.create_tree_list(
            expid,
            job_list_loader.jobs,
            None,
            dict(),
            False,
            job_list_loader.job_dictionary,
        )
        assert graph

        result = graph.create("dot", format="plain")
        assert result and len(result) > 0

    def test_process_graph(self, fixture_mock_basic_config):
        expid = "a003"
        experimentGraphDrawing = ExperimentGraphDrawing(expid)
        job_list_loader = JobListLoaderDirector(
            JobListLoaderBuilder(expid)
        ).build_loaded_joblist_loader()

        assert len(job_list_loader.jobs) == 8

        autosubmit_configuration_facade = ConfigurationFacadeDirector(
            AutosubmitConfigurationFacadeBuilder(expid)
        ).build_autosubmit_configuration_facade()

        # Create repository handler
        graph_draw_db = create_exp_graph_layout_repository(expid)

        # Delete content of table
        graph_draw_db.delete_all()

        experimentGraphDrawing.calculate_drawing(
            allJobs=job_list_loader.jobs,
            independent=False,
            num_chunks=autosubmit_configuration_facade.chunk_size,
            job_dictionary=job_list_loader.job_dictionary,
        )

        assert (
            isinstance(experimentGraphDrawing.coordinates, list)
            and len(experimentGraphDrawing.coordinates) == 8
        )

        rows = graph_draw_db.get_all()

        assert len(rows) == 8
        for job in rows:
            job_name: str = job.job_name
            assert job_name.startswith(expid)
