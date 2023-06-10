from dataclasses import dataclass
import json


@dataclass
class Status:
    status: str
    filename: str
    timestamp: str
    explanation: dict

    def is_done(self):
        return self.status == 'done'


if __name__ == '__main__':
    # Usage example
    status1 = Status('done', 'colorrabi.pptx', '2022-10-10', {'slide 1': 'you are awesome'})
