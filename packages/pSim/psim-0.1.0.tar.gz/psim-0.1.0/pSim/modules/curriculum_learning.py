import numpy as np
from scipy.spatial.distance import cdist


class CurriculumLearning:
    def __init__(self, plan, truncated_time=3600):
        self.plan = plan
        self.truncated_time = truncated_time
        self.t = 0

    def _generate_poses(
        self, n, x_min, x_max, y_min, y_max, t_min, t_max, reserved_poses
    ):
        xs = np.random.uniform(x_min, x_max, n)
        ys = np.random.uniform(y_min, y_max, n)
        ts = np.random.uniform(t_min, t_max, n)

        full_poses = np.array([xs, ys, ts]).T
        full_poses = np.vstack([full_poses, reserved_poses])
        dist_matrix = cdist(full_poses, full_poses)
        dist_matrix[np.tril_indices(n + len(reserved_poses))] = np.inf
        if dist_matrix.min() < 0.15:
            return self._generate_poses(
                n, x_min, x_max, y_min, y_max, t_min, t_max, reserved_poses
            )
        return full_poses[: -len(reserved_poses)]

    def _generate_pos(self, x_min, x_max, y_min, y_max):
        x = np.random.uniform(x_min, x_max)
        y = np.random.uniform(y_min, y_max)
        return x, y

    def get_states(self, simulator, num_ally_robots, num_enemy_robots):
        if self.plan == 0:
            simulator.vx, simulator.vy = 0.0, 0.0
            ball_pos = (0, 0)
            initial_poses = np.array(
                [
                    [-0.2, 0, 0],
                    [-0.4, -0.2, 0],
                    [-0.4, 0.2, 0],
                    [0.2, 0, np.pi],
                    [0.4, -0.2, np.pi],
                    [0.4, 0.2, np.pi],
                ],
                np.float64,
            )[: num_ally_robots + num_enemy_robots]

        elif self.plan == 1:
            simulator.vx, simulator.vy = 0.5, 0.5
            ball_pos = self._generate_pos(0.20, 0.50, -0.15, 0.15)
            reserved_poses = np.array([[ball_pos[0], ball_pos[1], 0]])
            current = self._generate_poses(
                1, -0.50, -0.20, -0.15, 0.15, -np.pi, np.pi, reserved_poses
            )
            if num_ally_robots + num_enemy_robots > 1:
                reserved_poses = np.vstack([current, reserved_poses])
                initial_poses = self._generate_poses(
                    num_ally_robots + num_enemy_robots - 1,
                    -0.7,
                    0.7,
                    -0.6,
                    0.6,
                    -np.pi,
                    np.pi,
                    reserved_poses,
                )
                initial_poses = np.vstack([current, initial_poses])
            else:
                initial_poses = current

        elif self.plan == 2:
            simulator.vx, simulator.vy = 0.6, 0.6
            ball_pos = self._generate_pos(-0.7, 0.7, -0.6, 0.6)
            reserved_poses = np.array([[ball_pos[0], ball_pos[1], 0]])
            initial_poses = self._generate_poses(
                num_ally_robots + num_enemy_robots,
                -0.7,
                0.7,
                -0.6,
                0.6,
                -np.pi,
                np.pi,
                reserved_poses,
            )

        elif self.plan == 3:
            simulator.vx, simulator.vy = 0.3, 0.0
            ball_pos = self._generate_pos(0.15, 0.3, -0.15, 0.15)
            reserved_poses = np.array([[ball_pos[0], ball_pos[1], 0]])
            initial_poses = self._generate_poses(
                num_ally_robots + num_enemy_robots,
                -0.20,
                0.20,
                -0.15,
                0.15,
                -np.pi,
                np.pi,
                reserved_poses,
            )

        return ball_pos, initial_poses

    def _cos_similarity(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def get_reward(self, simulator):
        r_goal = (
            0
            if simulator.ball_body.position.x < -0.765
            else 1
            if simulator.ball_body.position.x > 0.765
            else 0
        )
        terminated = r_goal != 0
        r_time = -1
        truncated = self.t == self.truncated_time
        if np.linalg.norm(simulator.ball_body.linearVelocity) > 0.05:
            similarity_center_ally = self._cos_similarity(
                simulator.ball_body.linearVelocity,
                np.array([-0.8, 0]) - simulator.ball_body.position,
            )
            similarity_center_enemy = self._cos_similarity(
                simulator.ball_body.linearVelocity,
                np.array([0.8, 0]) - simulator.ball_body.position,
            )
            r_sim = (
                np.tanh(similarity_center_enemy)
                - np.tanh(similarity_center_ally)
                - 3 * np.tanh(1)
            )
        else:
            r_sim = -5 * np.tanh(1)

        # if np.linalg.norm(simulator.robots_ally[0].linearVelocity) > 0.05:
        #     similarity_robot_ball = self._cos_similarity(
        #         simulator.robots_ally[0].linearVelocity,
        #         simulator.ball_body.position - simulator.robots_ally[0].position
        #     )
        #     r_robot = np.tanh(similarity_robot_ball)-2*np.tanh(1)
        # else:
        #     r_robot = - 3*np.tanh(1)

        # r_dis = -np.linalg.norm(
        #     simulator.robots_ally[0].position - simulator.ball_body.position
        # )
        # robot_ball_angle = np.arctan2(
        #     simulator.ball_body.position[1] - simulator.robots_ally[0].position[1],
        #     simulator.ball_body.position[0] - simulator.robots_ally[0].position[0]
        # )
        # r_theta = -np.abs(np.sin(simulator.robots_ally[0].angle - robot_ball_angle))
        # dis_goal = -np.linalg.norm(
        #     np.array([0.8, 0]) - simulator.ball_body.position
        # ) / 1.7

        r_contact_robot_ball = (
            0.5 if simulator.contact_listener.collision_robot_ball else 0
        )
        r_contact_robot_wall = (
            -1.0 if simulator.contact_listener.collision_robot_wall else 0
        )
        simulator.contact_listener.collision_robot_ball = False
        simulator.contact_listener.collision_robot_wall = False

        reward = np.array(
            [
                r_time,
                r_goal * 10,
                r_contact_robot_ball,
                r_contact_robot_wall,
                # r_dis/10,
                # r_theta/10,
                # dis_goal/10,
                r_sim,
                # r_robot,
            ]
        ).sum()

        return reward, terminated, truncated
