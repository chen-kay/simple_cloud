from cloud.fs.event.esl import esl_event


class Agent(object):
    def get_list(self):
        """列表
        """
        msg = "callcenter_config agent list"
        return esl_event.send(msg)

    def sign_in(self, user):
        '''签入
        '''
        msg = "callcenter_config agent set status {0} 'Available'".format(user)
        return esl_event.send(msg)

    def sign_out(self, user):
        '''签出
        '''
        msg = "callcenter_config agent set status {0} 'Logged Out'".format(
            user)
        return esl_event.send(msg)

    def in_queue(self, user, queue):
        '''进入队列
        '''
        self.sign_out(user)
        self.out_queue(user, queue)
        msg = 'callcenter_config tier add {0} {1} 1 1'.format(queue, user)
        return esl_event.send(msg)

    def out_queue(self, user, queue):
        '''离开队列
        '''
        msg = 'callcenter_config tier del {0} {1}'.format(queue, user)
        return esl_event.send(msg)

    def init_user(self, user):
        '''user初始化
        '''
        _del = self.del_user(user)
        if _del:
            msg = [
                "callcenter_config agent add {0} 'Callback'".format(user),
                "callcenter_config agent set contact {user} ${{sofia_contact(user/{user})}}"
                .format(user=user),
                "callcenter_config agent set ready_time {0} 2".format(user),
                "callcenter_config agent set wrap_up_time {0} 2".format(user),
                "callcenter_config agent set reject_delay_time {0} 2".format(
                    user),
            ]
            return esl_event.send(msg)
        return _del

    def del_user(self, user):
        '''user remove
        '''
        msg = 'callcenter_config agent del {0}'.format(user)
        return esl_event.send(msg)
