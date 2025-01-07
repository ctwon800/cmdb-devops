// import { request } from '@/api/service'

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      // tableType: 'vxe-table',
      // rowKey: true,
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      width: 240,
      fixed: 'right',
      view: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Retrieve')
        }
      },
      edit: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      },
      custom: [
        {
          thin: true,
          text: '远程连接',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-share',
          show () {
            return vm.hasPermissions('serverConnect')
          },
          emit: 'serverConnect'
        }
      ]
    },
    viewOptions: {
      componentType: 'form'
    },
    formOptions: {
      defaultSpan: 12 // 默认的表单 span
    },
    indexRow: { // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 60
    },
    columns: [
      {
        title: '平台',
        key: 'server_platform',
        width: 100,
        disabled: false,
        search: {
          disabled: false
        },
        type: 'radio',
        dict: {
          cache: true,
          url: '/api/cmdb/server_platform/',
          value: 'id',
          label: 'server_platform'
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '账号',
        key: 'account_name',
        width: 145,
        disabled: false,
        search: {
          disabled: false
        },
        type: 'select',
        dict: {
          cache: true,
          url: '/api/cmdb/account_management/',
          value: 'id',
          label: 'account_name'
        },
        form: {
          show: true,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'ID',
        key: 'id',
        disabled: true,
        form: {
          disabled: true
        }
      },
      {
        title: '实例id',
        key: 'instanceid',
        width: 145,
        dict: {
          data: vm.dictionary('instanceid')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '实例名称',
        key: 'instancename',
        width: 145,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('instancename')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '实例类型',
        key: 'instancetype',
        width: 145,
        dict: {
          data: vm.dictionary('instancetype')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '区域',
        key: 'region',
        width: 145,
        dict: {
          data: vm.dictionary('region')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '实例可用区',
        key: 'zone',
        width: 145,
        dict: {
          data: vm.dictionary('zone')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'os类型',
        key: 'ostype',
        width: 145,
        dict: {
          data: vm.dictionary('ostype')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'cpu',
        key: 'cpu',
        width: 145,
        dict: {
          data: vm.dictionary('cpu')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'memory',
        key: 'memory',
        width: 145,
        dict: {
          data: vm.dictionary('memory')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '公网ip',
        key: 'public_ip',
        width: 145,
        dict: {
          data: vm.dictionary('public_ip')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '内网ip',
        key: 'primary_ip',
        width: 145,
        dict: {
          data: vm.dictionary('primary_ip')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '运行状态',
        key: 'status',
        width: 145,
        dict: {
          data: vm.dictionary('status')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '过期时间',
        key: 'exprire_time',
        width: 145,
        dict: {
          data: vm.dictionary('exprire_time')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '远程连接关联账号',
        key: 'remote_auth',
        width: 100,
        disabled: false,
        search: {
          disabled: true
        },
        type: 'select',
        dict: {
          cache: true,
          url: '/api/cmdb/server_remote_account/',
          value: 'id',
          label: 'remote_name'
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      }
      // {
      //   title: '远程连接的登录账号',
      //   key: 'remote_auth',
      //   width: 145,
      //   type: 'input',
      //   form: {
      //     // show: true,
      //     component: {
      //       span: 12,
      //       showPassword: false,
      //       placeholder: '远程连接的登录账号'
      //     },
      //     editDisabled: false,
      //     itemProps: {
      //       class: { yxtInput: true }
      //     }
      //   },
      //   disabled: true
      // }
    ]
  }
}
