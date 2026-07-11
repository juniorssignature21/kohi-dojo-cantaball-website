                        +----------------+
                        |    Season      |
                        +----------------+
                        | id             |
                        | name           |
                        | start_date     |
                        | end_date       |
                        | is_active      |
                        +--------+-------+
                                 |
                                 | 1
                                 |
                                 | M
                      +----------v-----------+
                      |     LeagueWeek       |
                      +----------------------+
                      | id                   |
                      | season_id (FK)       |
                      | week_number          |
                      | registration_open    |
                      | registration_close   |
                      | max_teams (20)       |
                      | registered_teams     |
                      | status               |
                      +----------+-----------+
                                 |
                  +--------------+---------------+
                  |                              |
                1 |                            1 |
                  |                              |
                  | M                            | M
          +-------v--------+            +--------v--------+
          | Registration   |            |     Match       |
          +----------------+            +-----------------+
          | id             |            | id              |
          | week_id (FK)   |            | week_id (FK)    |
          | team_id (FK)   |            | team1_id (FK)   |
          | payment_id(FK) |            | team2_id (FK)   |
          | status         |            | team1_score     |
          | created_at     |            | team2_score     |
          +-------+--------+            | winner_id (FK)  |
                  |                     | played_at       |
                  |                     +-----------------+
                  |
                  |
                  |
          +-------v---------+
          |      Team       |
          +-----------------+
          | id              |
          | team_name       |
          | captain_phone   |
          | captain_email   |
          | logo            |
          | created_at      |
          +-------+---------+
                  |
          +-------+-------+
          |               |
        1 |             1 |
          |               |
          | M             M
+---------v------+ +------v----------+
| TeamPlayer     | |    Payment      |
+----------------+ +-----------------+
| id             | | id              |
| team_id (FK)   | | team_id (FK)    |
| player_name    | | amount          |
| phone          | | reference       |
| email          | | gateway         |
| is_captain     | | status          |
+----------------+ | paid_at         |
                   +-----------------+