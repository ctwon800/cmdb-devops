// import { request } from '@/api/service'

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      dropdown: { // 操作列折叠
        atLeast: 3, // 至少几个以上的按钮才会被折叠,注意show=false的按钮也会计算在内（行编辑按钮默认是隐藏的也会占一个位置）
        text: '更多', // dropdown按钮文字
        type: 'primary'
      },
      width: 360,
      view: {
        show: false
      },
      edit: {
        show: false
      },
      remove: {
        show: false
      },
      custom: [
        {
          thin: true,
          text: '详情',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-view',
          show () {
            return vm.hasPermissions('nodeDetail')
          },
          emit: 'nodeDetail',
          order: 1
        },
        {
          thin: true,
          text: '调度配置',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-view',
          show () {
            return vm.hasPermissions('nodeSchedule')
          },
          emit: 'nodeSchedule',
          order: 1
        },
        {
          thin: true,
          icon: 'el-icon-refresh-right',
          text: '标签管理',
          emit: 'nodeLabel',
          size: 'small',
          show () {
            return vm.hasPermissions('nodeLabel')
          }
        },
        {
          thin: true,
          icon: 'el-icon-refresh-right',
          text: '污点管理',
          emit: 'nodeTaint',
          size: 'small',
          show () {
            return vm.hasPermissions('nodeTaint')
          }
        },
        {
          thin: true,
          icon: 'el-icon-refresh-right',
          text: '节点排水',
          emit: 'nodeDrain',
          size: 'small',
          show () {
            return vm.hasPermissions('nodeDrain')
          }
        },
        {
          icon: 'el-icon-delete',
          text: '移除',
          emit: 'nodeDelete',
          size: 'small',
          show () {
            return vm.hasPermissions('nodeDelete')
          }
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
        title: '集群名称',
        key: 'k8s_cluster_name',
        width: 145,
        disabled: true,
        search: {
          disabled: false,
          props: {
            clearable: true
          }
        },
        type: 'select',
        dict: {
          cache: false,
          url: '/api/container/cluster/',
          value: 'k8s_cluster_name'
        },
        form: {
          show: true
        }
      },
      {
        title: '节点名称',
        key: 'node_name',
        width: 180,
        search: {
          disabled: false
        },
        dict: {
          cache: false,
          data: vm.dictionary('node_name')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '状态',
        key: 'node_status',
        width: 80,
        dict: {
          cache: false,
          data: vm.dictionary('node_status')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '所属集群',
        key: 'cluster_name',
        width: 145,
        disabled: false,
        search: {
          disabled: true
        },
        dict: {
          cache: false,
          data: vm.dictionary('cluster_name')
        },
        form: {
          show: true
        }
      },
      {
        title: '实例ip',
        key: 'node_ip',
        width: 100,
        dict: {
          cache: false,
          data: vm.dictionary('node_ip')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '调度状态',
        key: 'node_schedule',
        width: 80,
        // sortable: true,
        type: 'select',
        dict: {
          cache: false,
          data: [
            { value: 'True', label: '暂停调度' },
            { value: 'False', label: '可调度' }
          ]
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'kubectl_version',
        key: 'kubectl_version',
        width: 145,
        dict: {
          cache: false,
          data: vm.dictionary('kubectl_version')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '容器运行时',
        key: 'container_runtime_version',
        width: 145,
        dict: {
          cache: false,
          data: vm.dictionary('container_runtime_version')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      }
    ]
  }
}
